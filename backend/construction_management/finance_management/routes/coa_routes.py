import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from extensions import db
from finance_management.models.chart_of_accounts import ChartOfAccounts
from user_management.models import User
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, not_found_response, paginated_response, server_error_response

logger = logging.getLogger(__name__)

coa_bp = Blueprint('coa', __name__)


@coa_bp.route('/coa', methods=['GET'])
@jwt_required()
def get_chart_of_accounts():
    """Get all chart of accounts for company with pagination"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return not_found_response("User")

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        # Query with filters
        query = ChartOfAccounts.query.filter_by(company_id=user.company_id)

        # Filter by type if provided
        account_type = request.args.get('type')
        if account_type:
            query = query.filter_by(account_type=account_type)

        # Filter by active status
        is_active = request.args.get('is_active')
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')

        paginated = query.paginate(page=page, per_page=per_page)

        data = {
            'accounts': [acc.to_dict() for acc in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }

        return success_response(data, "Chart of accounts retrieved")

    except Exception as e:
        logger.error(f"Error fetching chart of accounts: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve chart of accounts")


@coa_bp.route('/coa/<int:account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    """Get single account with details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        account = ChartOfAccounts.query.filter_by(
            id=account_id,
            company_id=user.company_id
        ).first()

        if not account:
            return not_found_response("Account")

        data = account.to_dict()
        # Include parent account info if exists
        if account.parent_account_id:
            parent = ChartOfAccounts.query.get(account.parent_account_id)
            data['parent_account'] = {
                'id': parent.id,
                'code': parent.account_code,
                'name': parent.name
            } if parent else None

        return success_response(data, "Account retrieved")

    except Exception as e:
        logger.error(f"Error fetching account {account_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve account")


@coa_bp.route('/coa', methods=['POST'])
@jwt_required()
def create_account():
    """Create new chart of account"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json()

        # Validation
        errors = []
        if not data.get('account_code'):
            errors.append("Account code is required")
        if not data.get('name'):
            errors.append("Account name is required")
        if not data.get('account_type'):
            errors.append("Account type is required")
        if data.get('account_type') not in ['asset', 'liability', 'equity', 'revenue', 'expense']:
            errors.append("Invalid account type")
        if not data.get('category'):
            errors.append("Category is required")

        if errors:
            return error_response(errors, 400)

        # Check duplicate account code
        existing = ChartOfAccounts.query.filter_by(
            account_code=data['account_code'],
            company_id=user.company_id
        ).first()

        if existing:
            return error_response("Account code already exists", 400)

        account = ChartOfAccounts(
            account_code=data['account_code'],
            name=data['name'],
            account_type=data['account_type'],
            category=data['category'],
            description=data.get('description'),
            parent_account_id=data.get('parent_account_id'),
            is_active=data.get('is_active', True),
            company_id=user.company_id
        )

        db.session.add(account)
        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            entity_type='ChartOfAccounts',
            entity_id=account.id,
            action='create',
            description=f'Created account {account.account_code}'
        )

        return success_response(account.to_dict(), "Account created", 201)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating account: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create account")


@coa_bp.route('/coa/<int:account_id>', methods=['PUT'])
@jwt_required()
def update_account(account_id):
    """Update chart of account"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        account = ChartOfAccounts.query.filter_by(
            id=account_id,
            company_id=user.company_id
        ).first()

        if not account:
            return not_found_response("Account")

        data = request.get_json()

        # Update fields
        if 'name' in data:
            account.name = data['name']
        if 'category' in data:
            account.category = data['category']
        if 'description' in data:
            account.description = data['description']
        if 'is_active' in data:
            account.is_active = data['is_active']
        if 'parent_account_id' in data:
            account.parent_account_id = data['parent_account_id']

        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            entity_type='ChartOfAccounts',
            entity_id=account.id,
            action='update',
            description=f'Updated account {account.account_code}'
        )

        return success_response(account.to_dict(), "Account updated")

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating account {account_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update account")


@coa_bp.route('/coa/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_account(account_id):
    """Delete chart of account (soft delete by deactivating)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        account = ChartOfAccounts.query.filter_by(
            id=account_id,
            company_id=user.company_id
        ).first()

        if not account:
            return not_found_response("Account")

        # Check if account has child accounts
        children = ChartOfAccounts.query.filter_by(parent_account_id=account_id).count()
        if children > 0:
            return error_response("Cannot delete account with sub-accounts", 400)

        # Soft delete by deactivating
        account.is_active = False
        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            entity_type='ChartOfAccounts',
            entity_id=account.id,
            action='delete',
            description=f'Deleted account {account.account_code}'
        )

        return success_response(None, "Account deleted")

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting account {account_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete account")


@coa_bp.route('/coa/by-type/<account_type>', methods=['GET'])
@jwt_required()
def get_accounts_by_type(account_type):
    """Get accounts filtered by type"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        valid_types = ['asset', 'liability', 'equity', 'revenue', 'expense']
        if account_type not in valid_types:
            return error_response(f"Invalid account type. Must be one of: {', '.join(valid_types)}", 400)

        accounts = ChartOfAccounts.query.filter_by(
            account_type=account_type,
            company_id=user.company_id,
            is_active=True
        ).all()

        data = [acc.to_dict() for acc in accounts]
        return success_response(data, f"Accounts of type '{account_type}' retrieved")

    except Exception as e:
        logger.error(f"Error fetching accounts by type '{account_type}': {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve accounts by type")


@coa_bp.route('/coa/hierarchy', methods=['GET'])
@jwt_required()
def get_coa_hierarchy():
    """Get hierarchical chart of accounts (parent-child structure)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        # Get only root accounts (parent_account_id is NULL)
        root_accounts = ChartOfAccounts.query.filter_by(
            parent_account_id=None,
            company_id=user.company_id,
            is_active=True
        ).all()

        def build_hierarchy(account):
            """Recursively build account hierarchy"""
            acc_dict = account.to_dict()
            # Get child accounts
            children = ChartOfAccounts.query.filter_by(
                parent_account_id=account.id,
                is_active=True
            ).all()
            acc_dict['children'] = [build_hierarchy(child) for child in children]
            return acc_dict

        hierarchy = [build_hierarchy(acc) for acc in root_accounts]
        return success_response(hierarchy, "Chart hierarchy retrieved")

    except Exception as e:
        logger.error(f"Error fetching CoA hierarchy: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve chart hierarchy")
