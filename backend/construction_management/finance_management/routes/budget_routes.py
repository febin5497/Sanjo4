import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from extensions import db
from finance_management.models.budget import Budget, BudgetCategory, BudgetApprovalRequest
from finance_management.models.cash_transaction import CashTransaction
from user_management.models import User
from project_management.models.models import Project
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, not_found_response, paginated_response, server_error_response

logger = logging.getLogger(__name__)

budget_bp = Blueprint('budget', __name__)


# ✅ Get all budgets for a project or company
@budget_bp.route('/budgets', methods=['GET'])
@jwt_required()
def get_budgets():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        project_id = request.args.get('project_id', None, type=int)
        status = request.args.get('status', None, type=str)

        query = Budget.query.filter_by(company_id=user.company_id) if user else Budget.query

        if project_id:
            query = query.filter_by(project_id=project_id)
        if status:
            query = query.filter_by(status=status)

        total = query.count()
        budgets = query.paginate(page=page, per_page=per_page).items

        data = [budget.to_dict(include_categories=True) for budget in budgets]

        return paginated_response(
            data,
            total,
            page,
            per_page,
            "Budgets retrieved",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error fetching budgets: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve budgets")


# ✅ Get single budget with details
@budget_bp.route('/budgets/<int:budget_id>', methods=['GET'])
@jwt_required()
def get_budget(budget_id):
    try:
        budget = Budget.query.get(budget_id)

        if not budget:
            return not_found_response("Budget")

        return success_response(budget.to_dict(include_categories=True), "Budget retrieved", status_code=200)
    except Exception as e:
        logger.error(f"Error fetching budget {budget_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve budget")


# ✅ Create new budget
@budget_bp.route('/budgets', methods=['POST'])
@jwt_required()
def create_budget():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        # Validation
        errors = []
        if not data.get('project_id'):
            errors.append({"field": "project_id", "message": "Project ID is required"})
        if not data.get('total_budget'):
            errors.append({"field": "total_budget", "message": "Total budget is required"})
        if not data.get('start_date'):
            errors.append({"field": "start_date", "message": "Start date is required"})
        if not data.get('categories') or len(data.get('categories', [])) == 0:
            errors.append({"field": "categories", "message": "At least one budget category is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Verify project exists
        project = Project.query.get(data.get('project_id'))
        if not project:
            return not_found_response("Project")

        # Create budget
        budget = Budget(
            project_id=data.get('project_id'),
            total_budget=data.get('total_budget'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            description=data.get('description'),
            notes=data.get('notes'),
            created_by_id=user_id,
            company_id=user.company_id if user else None
        )

        # Add categories
        categories_data = data.get('categories', [])
        total_allocated = sum(cat.get('allocated_amount', 0) for cat in categories_data)

        if total_allocated > budget.total_budget:
            return error_response(
                f"Total allocated (₹{total_allocated}) exceeds total budget (₹{budget.total_budget})",
                status_code=400
            )

        for cat_data in categories_data:
            category = BudgetCategory(
                category=cat_data.get('category'),
                allocated_amount=cat_data.get('allocated_amount'),
                warning_threshold=cat_data.get('warning_threshold', 80)
            )
            budget.categories.append(category)

        db.session.add(budget)
        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=user_id,
            company_id=user.company_id if user else None,
            entity_type='Budget',
            entity_id=budget.id,
            action='CREATE',
            new_values={
                'project_id': budget.project_id,
                'total_budget': budget.total_budget,
                'categories': len(budget.categories)
            },
            entity_name=f"Budget for Project #{budget.project_id}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(budget.to_dict(include_categories=True), "Budget created", status_code=201)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating budget: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create budget")


# ✅ Update budget
@budget_bp.route('/budgets/<int:budget_id>', methods=['PUT'])
@jwt_required()
def update_budget(budget_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        budget = Budget.query.get(budget_id)
        if not budget:
            return not_found_response("Budget")

        # Update fields
        if 'description' in data:
            budget.description = data.get('description')
        if 'notes' in data:
            budget.notes = data.get('notes')
        if 'status' in data:
            budget.status = data.get('status')

        # Update categories if provided
        if 'categories' in data:
            # Remove old categories
            BudgetCategory.query.filter_by(budget_id=budget_id).delete()

            # Add new categories
            categories_data = data.get('categories', [])
            total_allocated = sum(cat.get('allocated_amount', 0) for cat in categories_data)

            if total_allocated > budget.total_budget:
                db.session.rollback()
                return error_response(
                    f"Total allocated exceeds total budget",
                    status_code=400
                )

            for cat_data in categories_data:
                category = BudgetCategory(
                    category=cat_data.get('category'),
                    allocated_amount=cat_data.get('allocated_amount'),
                    warning_threshold=cat_data.get('warning_threshold', 80)
                )
                budget.categories.append(category)

        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=user_id,
            company_id=user.company_id if user else None,
            entity_type='Budget',
            entity_id=budget.id,
            action='UPDATE',
            new_values={'status': budget.status},
            entity_name=f"Budget for Project #{budget.project_id}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(budget.to_dict(include_categories=True), "Budget updated", status_code=200)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating budget {budget_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update budget")


# ✅ Get budget vs actual comparison
@budget_bp.route('/budgets/<int:budget_id>/vs-actual', methods=['GET'])
@jwt_required()
def get_budget_vs_actual(budget_id):
    try:
        budget = Budget.query.get(budget_id)
        if not budget:
            return not_found_response("Budget")

        # Get all transactions for this budget's project
        transactions = CashTransaction.query.filter_by(project_id=budget.project_id).all()

        # Group by category
        actual_by_category = {}
        for txn in transactions:
            cat = txn.category
            if cat not in actual_by_category:
                actual_by_category[cat] = 0
            if txn.type == 'expense':
                actual_by_category[cat] += txn.amount

        # Build response
        categories_data = []
        for cat in budget.categories:
            actual = actual_by_category.get(cat.category, 0)
            variance = cat.allocated_amount - actual
            categories_data.append({
                'category': cat.category,
                'allocated': cat.allocated_amount,
                'actual': actual,
                'variance': variance,
                'variance_percent': (variance / cat.allocated_amount * 100) if cat.allocated_amount > 0 else 0,
                'status': 'on_track' if actual <= cat.allocated_amount else 'overrun'
            })

        response = {
            'budget_id': budget.id,
            'project_id': budget.project_id,
            'total_allocated': sum(c['allocated'] for c in categories_data),
            'total_actual': sum(c['actual'] for c in categories_data),
            'total_variance': sum(c['variance'] for c in categories_data),
            'categories': categories_data
        }

        return success_response(response, "Budget vs actual retrieved", status_code=200)

    except Exception as e:
        logger.error(f"Error fetching budget vs actual for budget {budget_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve budget comparison")


# ✅ Check budget warning before creating transaction
@budget_bp.route('/budgets/<int:budget_id>/check-budget', methods=['POST'])
@jwt_required()
def check_budget_warning(budget_id):
    try:
        data = request.get_json(silent=True) or {}

        budget = Budget.query.get(budget_id)
        if not budget:
            return not_found_response("Budget")

        category = data.get('category')
        amount = data.get('amount', 0)

        # Find matching category
        budget_cat = next((c for c in budget.categories if c.category == category), None)
        if not budget_cat:
            return success_response({
                'warning': False,
                'exceeded': False,
                'message': f'Category "{category}" not found in budget'
            })

        # Check if adding this amount would exceed budget
        new_total = budget_cat.used_amount + amount
        exceeded = new_total > budget_cat.allocated_amount
        warning = budget_cat.get_utilization_percent() >= budget_cat.warning_threshold

        response = {
            'warning': warning or exceeded,
            'exceeded': exceeded,
            'allocated': budget_cat.allocated_amount,
            'current_used': budget_cat.used_amount,
            'would_be_used': new_total,
            'remaining': budget_cat.allocated_amount - budget_cat.used_amount,
            'message': None
        }

        if exceeded:
            response['message'] = f"Amount would exceed budget. Remaining: ₹{budget_cat.get_remaining()}"
        elif warning:
            response['message'] = f"Approaching budget limit. {budget_cat.get_utilization_percent():.1f}% used"

        return success_response(response, "Budget check completed", status_code=200)

    except Exception as e:
        logger.error(f"Error checking budget {budget_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to check budget")


# ✅ Delete budget
@budget_bp.route('/budgets/<int:budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        budget = Budget.query.get(budget_id)
        if not budget:
            return not_found_response("Budget")

        # Log activity
        log_entity_action(
            user_id=user_id,
            company_id=user.company_id if user else None,
            entity_type='Budget',
            entity_id=budget.id,
            action='DELETE',
            new_values={'status': 'deleted'},
            entity_name=f"Budget for Project #{budget.project_id}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        db.session.delete(budget)
        db.session.commit()

        return success_response(None, "Budget deleted", status_code=200)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting budget {budget_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete budget")
