import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from extensions import db
from finance_management.models.cash_transaction import CashTransaction
from finance_management.models.invoice import Invoice
from finance_management.models.budget import Budget, BudgetCategory
from user_management.models import User
from project_management.models.models import Project
from utils.response_formatter import success_response, error_response, not_found_response, server_error_response

logger = logging.getLogger(__name__)

reporting_bp = Blueprint('reporting', __name__)

@reporting_bp.route('/reports/project-profitability', methods=['GET'])
@jwt_required()
def project_profitability():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        project_id = request.args.get('project_id', type=int)

        # If project_id provided, return data for that project
        if project_id:
            revenue = db.session.query(db.func.sum(Invoice.total)).filter_by(
                project_id=project_id, company_id=user.company_id
            ).scalar() or 0

            expenses = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(
                type='expense', project_id=project_id, company_id=user.company_id
            ).scalar() or 0

            profit = revenue - expenses
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0

            return success_response([{
                'id': project_id,
                'name': f'Project {project_id}',
                'revenue': float(revenue),
                'expenses': float(expenses),
                'profit': float(profit),
                'margin': round(profit_margin, 2)
            }], "Profitability report", status_code=200)

        # If no project_id, return data for ALL projects
        projects = Project.query.filter_by(company_id=user.company_id).all()
        report_data = []

        for project in projects:
            revenue = db.session.query(db.func.sum(Invoice.total)).filter_by(
                project_id=project.id, company_id=user.company_id
            ).scalar() or 0

            expenses = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(
                type='expense', project_id=project.id, company_id=user.company_id
            ).scalar() or 0

            profit = revenue - expenses
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0

            report_data.append({
                'id': project.id,
                'name': project.name,
                'revenue': float(revenue),
                'expenses': float(expenses),
                'profit': float(profit),
                'margin': round(profit_margin, 2)
            })

        return success_response(report_data, "Profitability report", status_code=200)
    except Exception as e:
        logger.error(f"Error generating profitability report: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to generate profitability report")

@reporting_bp.route('/reports/cost-vs-budget', methods=['GET'])
@jwt_required()
def cost_vs_budget():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        project_id = request.args.get('project_id', type=int)

        # If project_id provided, return detailed data for that project
        if project_id:
            budget = Budget.query.filter_by(project_id=project_id, company_id=user.company_id).first()
            if not budget:
                return not_found_response("Budget", details="for this project")

            categories_data = []
            for cat in budget.categories:
                actual = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(
                    category=cat.category, project_id=project_id, type='expense', company_id=user.company_id
                ).scalar() or 0

                variance = cat.allocated_amount - actual
                categories_data.append({
                    'category': cat.category,
                    'budget': float(cat.allocated_amount),
                    'spent': float(actual),
                    'variance': float(variance),
                    'percent_used': round((actual / cat.allocated_amount * 100) if cat.allocated_amount > 0 else 0, 2)
                })

            return success_response({
                'budget_id': budget.id,
                'project_id': project_id,
                'total_budget': sum(c['budget'] for c in categories_data),
                'total_spent': sum(c['spent'] for c in categories_data),
                'summary': {
                    'total_budget': sum(c['budget'] for c in categories_data),
                    'total_spent': sum(c['spent'] for c in categories_data),
                    'variance': sum(c['budget'] for c in categories_data) - sum(c['spent'] for c in categories_data)
                },
                'categories': categories_data
            }, "Cost vs budget report", status_code=200)

        # If no project_id, return summary for ALL projects with budgets
        budgets = Budget.query.filter_by(company_id=user.company_id).all()
        categories_summary = {}
        total_allocated = 0
        total_spent = 0

        for budget in budgets:
            for cat in budget.categories:
                actual = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(
                    category=cat.category, project_id=budget.project_id, type='expense', company_id=user.company_id
                ).scalar() or 0

                if cat.category not in categories_summary:
                    categories_summary[cat.category] = {'budget': 0, 'spent': 0}

                categories_summary[cat.category]['budget'] += cat.allocated_amount
                categories_summary[cat.category]['spent'] += actual
                total_allocated += cat.allocated_amount
                total_spent += actual

        report_data = []
        for category, values in categories_summary.items():
            variance = values['budget'] - values['spent']
            report_data.append({
                'category': category,
                'budget': float(values['budget']),
                'spent': float(values['spent']),
                'variance': float(variance),
                'percent_used': round((values['spent'] / values['budget'] * 100) if values['budget'] > 0 else 0, 2)
            })

        return success_response({
            'summary': {
                'total_budget': total_allocated,
                'total_spent': total_spent,
                'variance': total_allocated - total_spent
            },
            'categories': report_data
        }, "Cost vs budget report", status_code=200)
    except Exception as e:
        logger.error(f"Error generating cost vs budget report: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to generate cost vs budget report")

@reporting_bp.route('/reports/cash-flow', methods=['GET'])
@jwt_required()
def cash_flow():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        days = request.args.get('days', 30, type=int)
        project_id = request.args.get('project_id', type=int)

        start_date = datetime.utcnow().date() - timedelta(days=days)

        query = CashTransaction.query.filter(
            CashTransaction.date >= start_date,
            CashTransaction.company_id == user.company_id
        )
        if project_id:
            query = query.filter_by(project_id=project_id)

        transactions = query.all()

        daily_flow = {}
        for txn in transactions:
            date_key = txn.date.isoformat()
            if date_key not in daily_flow:
                daily_flow[date_key] = {'income': 0, 'expense': 0}

            if txn.type == 'income':
                daily_flow[date_key]['income'] += txn.amount
            else:
                daily_flow[date_key]['expense'] += txn.amount

        report_data = []
        for date_key in sorted(daily_flow.keys()):
            flow = daily_flow[date_key]
            report_data.append({
                'date': date_key,
                'inflow': float(flow['income']),
                'outflow': float(flow['expense']),
                'balance': float(flow['income'] - flow['expense'])
            })

        # Return report_data as the main data array, with summary info
        return success_response(report_data, "Cash flow report", status_code=200)
    except Exception as e:
        logger.error(f"Error generating cash flow report: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to generate cash flow report")

@reporting_bp.route('/reports/receivables-aging', methods=['GET'])
@jwt_required()
def receivables_aging():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        today = datetime.utcnow().date()

        invoices = Invoice.query.filter_by(
            status='pending', company_id=user.company_id
        ).all()

        aging = {
            'current': {'count': 0, 'amount': 0},
            '30_days': {'count': 0, 'amount': 0},
            '60_days': {'count': 0, 'amount': 0},
            '90_days': {'count': 0, 'amount': 0}
        }

        for inv in invoices:
            days_overdue = (today - inv.due_date).days
            if days_overdue <= 0:
                aging['current']['count'] += 1
                aging['current']['amount'] += inv.total
            elif days_overdue <= 30:
                aging['30_days']['count'] += 1
                aging['30_days']['amount'] += inv.total
            elif days_overdue <= 60:
                aging['60_days']['count'] += 1
                aging['60_days']['amount'] += inv.total
            else:
                aging['90_days']['count'] += 1
                aging['90_days']['amount'] += inv.total

        # Convert to array format for frontend
        total_amount = sum(bucket['amount'] for bucket in aging.values())
        aging_buckets = []
        bucket_names = {
            'current': 'Current (0-30)',
            '30_days': 'Overdue (31-60)',
            '60_days': 'Overdue (61-90)',
            '90_days': 'Long Overdue (90+)'
        }

        summary = {
            'total': float(total_amount),
            'current': float(aging['current']['amount']),
            'thirty_plus': float(aging['30_days']['amount'] + aging['60_days']['amount']),
            'ninety_plus': float(aging['90_days']['amount'])
        }

        for key, bucket_name in bucket_names.items():
            bucket = aging[key]
            aging_buckets.append({
                'bucket': bucket_name,
                'invoice_count': bucket['count'],
                'amount': float(bucket['amount']),
                'percent': round((bucket['amount'] / total_amount * 100) if total_amount > 0 else 0, 2)
            })

        return success_response({
            'summary': summary,
            'aging_buckets': aging_buckets
        }, "Receivables aging report", status_code=200)
    except Exception as e:
        logger.error(f"Error generating receivables aging report: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to generate receivables aging report")
