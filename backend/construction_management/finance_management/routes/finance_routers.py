"""
Specialized Finance Routers - Using BaseResourceRouter

Auto-generates CRUD endpoints for finance entities:
- Chart of Accounts
- Budgets
- Budget Categories
- Retention tracking

Consolidates explicit route implementations in:
- coa_routes.py
- budget_routes.py
"""

import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from base.base_resource_router import BaseResourceRouter
from extensions import db
from finance_management.models.chart_of_accounts import ChartOfAccounts
from finance_management.models.budget import Budget
from user_management.models import User
from utils.response_formatter import success_response, error_response, not_found_response, server_error_response

logger = logging.getLogger(__name__)


# ==================== Chart of Accounts Router ====================

class ChartOfAccountsRouter(BaseResourceRouter):
    """Auto-generates CoA CRUD endpoints"""
    model = ChartOfAccounts
    entity_name = "Chart of Accounts"
    searchable_fields = ['account_code', 'name', 'category']

    @classmethod
    def schema(cls, obj):
        """Schema for CoA responses"""
        return {
            'id': obj.id,
            'account_code': obj.account_code,
            'name': obj.name,
            'type': obj.account_type,
            'category': obj.category,
            'description': obj.description,
            'is_active': obj.is_active,
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate CoA creation"""
        errors = []
        if not data.get('account_code'):
            errors.append({'field': 'account_code', 'message': 'Account code required'})
        if not data.get('name'):
            errors.append({'field': 'name', 'message': 'Account name required'})
        if not data.get('account_type'):
            errors.append({'field': 'account_type', 'message': 'Account type required'})
        if data.get('account_type') not in ['asset', 'liability', 'equity', 'revenue', 'expense']:
            errors.append({'field': 'account_type', 'message': 'Invalid account type'})
        if not data.get('category'):
            errors.append({'field': 'category', 'message': 'Category required'})
        return errors

    @classmethod
    @jwt_required()
    def get_by_type(cls):
        """Custom endpoint: Get accounts by type"""
        try:
            account_type = request.args.get('type', type=str)
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not account_type:
                return error_response("Type parameter required", 400)

            valid_types = ['asset', 'liability', 'equity', 'revenue', 'expense']
            if account_type not in valid_types:
                return error_response(f"Invalid type. Must be: {', '.join(valid_types)}", 400)

            accounts = cls.model.query.filter_by(
                account_type=account_type,
                company_id=user.company_id,
                is_active=True
            ).all()

            return success_response(
                [cls.schema(acc) for acc in accounts],
                f"Accounts of type '{account_type}' retrieved"
            )
        except ValueError as e:
            return error_response(f"Invalid input: {str(e)}", status_code=400)
        except Exception as e:
            logger.error(f"Error fetching accounts by type: {str(e)}", exc_info=True)
            return server_error_response(details="Failed to retrieve accounts by type")

    @classmethod
    @jwt_required()
    def get_hierarchy(cls):
        """Custom endpoint: Get hierarchical CoA"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            def build_hierarchy(account):
                """Recursively build account hierarchy"""
                acc_dict = cls.schema(account)
                children = cls.model.query.filter_by(
                    parent_account_id=account.id,
                    is_active=True
                ).all()
                acc_dict['children'] = [build_hierarchy(child) for child in children]
                return acc_dict

            root_accounts = cls.model.query.filter_by(
                parent_account_id=None,
                company_id=user.company_id,
                is_active=True
            ).all()

            hierarchy = [build_hierarchy(acc) for acc in root_accounts]
            return success_response(hierarchy, "Chart hierarchy retrieved")
        except Exception as e:
            logger.error(f"Error fetching chart hierarchy: {str(e)}", exc_info=True)
            return server_error_response(details="Failed to retrieve chart hierarchy")


# ==================== Budget Router ====================

class BudgetRouter(BaseResourceRouter):
    """Auto-generates Budget CRUD endpoints"""
    model = Budget
    entity_name = "Budget"
    searchable_fields = ['description']

    @classmethod
    def schema(cls, obj):
        """Schema for Budget responses"""
        return {
            'id': obj.id,
            'project_id': obj.project_id,
            'description': obj.description,
            'total_budget': float(obj.total_budget),
            'allocated_total': float(obj.get_total_allocated()) if hasattr(obj, 'get_total_allocated') else 0,
            'spent_total': float(obj.get_total_spent()) if hasattr(obj, 'get_total_spent') else 0,
            'variance': float(obj.get_variance()) if hasattr(obj, 'get_variance') else 0,
            'utilization_percent': float(obj.get_utilization_percent()) if hasattr(obj, 'get_utilization_percent') else 0,
            'status': obj.status,
            'start_date': obj.start_date.isoformat() if obj.start_date else None,
            'end_date': obj.end_date.isoformat() if obj.end_date else None,
            'approved_by_id': obj.approved_by_id,
            'approved_at': obj.approved_at.isoformat() if obj.approved_at else None,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'created_by_id': obj.created_by_id
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Budget creation"""
        errors = []
        if not data.get('project_id'):
            errors.append({'field': 'project_id', 'message': 'Project ID required'})
        if not data.get('total_budget'):
            errors.append({'field': 'total_budget', 'message': 'Total budget amount required'})
        if not data.get('description'):
            errors.append({'field': 'description', 'message': 'Description required'})
        if not data.get('start_date'):
            errors.append({'field': 'start_date', 'message': 'Start date required'})
        return errors


# ==================== Register Routers ====================

def register_finance_routers(app):
    """Register all finance routers with Flask app"""
    # Chart of Accounts
    coa_bp = ChartOfAccountsRouter.create_blueprint(url_prefix='/api/finance/coa')
    coa_bp.add_url_rule('/by-type', 'coa_by_type', ChartOfAccountsRouter.get_by_type, methods=['GET'])
    coa_bp.add_url_rule('/hierarchy', 'coa_hierarchy', ChartOfAccountsRouter.get_hierarchy, methods=['GET'])
    app.register_blueprint(coa_bp)

    # Budget
    budget_bp = BudgetRouter.create_blueprint(url_prefix='/api/finance/budgets')
    app.register_blueprint(budget_bp)
