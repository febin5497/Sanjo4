from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from extensions import db
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from finance_management.models.cash_transaction import CashTransaction
from finance_management.models.budget import Budget, BudgetCategory
from user_management.models import User
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import (
    success_response, error_response, server_error_response, not_found_response, paginated_response
)

logger = logging.getLogger(__name__)

finance_bp = Blueprint('finance', __name__)


# ✅ Add a new transaction
@finance_bp.route('/transaction', methods=['POST'])
@jwt_required()
def add_transaction():
    try:
        data = request.get_json(silent=True) or {}
        user_id = get_jwt_identity()

        # Validate required fields
        errors = []
        if not data.get('date'):
            errors.append({"field": "date", "message": "Date is required"})
        if not data.get('type'):
            errors.append({"field": "type", "message": "Transaction type is required"})
        account_code = data.get('account_code')
        category = data.get('category')
        if not category and not account_code:
            errors.append({"field": "category", "message": "Category or account_code is required"})
        if not data.get('amount'):
            errors.append({"field": "amount", "message": "Amount is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Auto-fill category from Chart of Accounts if account_code provided
        if account_code:
            coa_entry = ChartOfAccounts.query.filter_by(account_code=account_code, is_active=True).first()
            if coa_entry:
                if not category:
                    category = coa_entry.category
            else:
                errors.append({"field": "account_code", "message": "Account code not found"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        transaction = CashTransaction(
            project_id=data.get('project_id'),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            type=data['type'],
            category=category,
            account_code=account_code,
            amount=data['amount'],
            description=data.get('description'),
            created_by=user_id
        )
        db.session.add(transaction)
        db.session.flush()

        # Sync budget category used_amount for expense transactions with a project
        if transaction.type == 'expense' and transaction.project_id and transaction.category:
            budget = Budget.query.filter_by(project_id=transaction.project_id, status='active').first()
            if budget:
                category = BudgetCategory.query.filter_by(
                    budget_id=budget.id,
                    category=transaction.category
                ).first()
                if category:
                    category.used_amount = (category.used_amount or 0) + abs(transaction.amount)

        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='CashTransaction',
            entity_id=transaction.id,
            action='CREATE',
            new_values={
                'id': transaction.id,
                'project_id': transaction.project_id,
                'date': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
                'type': transaction.type,
                'category': transaction.category,
                'amount': transaction.amount,
                'description': transaction.description
            },
            entity_name=f"{transaction.type.upper()} - {transaction.category}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        response_data = {
            'id': transaction.id,
            'project_id': transaction.project_id,
            'date': transaction.date.strftime('%Y-%m-%d'),
            'type': transaction.type,
            'category': transaction.category,
            'amount': transaction.amount,
            'description': transaction.description
        }

        return success_response(response_data, "Transaction added successfully", status_code=201)
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except TypeError as e:
        db.session.rollback()
        return error_response("Invalid data type in request", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Add transaction error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to add transaction")


# ✅ Update an existing transaction
@finance_bp.route('/transaction/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    try:
        transaction = CashTransaction.query.get(transaction_id)
        if not transaction:
            return not_found_response("Transaction", details=f"No transaction with ID {transaction_id} found")

        # Capture old values BEFORE update
        old_values = {
            'id': transaction.id,
            'project_id': transaction.project_id,
            'date': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
            'type': transaction.type,
            'category': transaction.category,
            'amount': transaction.amount,
            'description': transaction.description
        }

        data = request.get_json(silent=True) or {}
        transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        transaction.type = data['type']
        transaction.category = data.get('category', transaction.category)
        transaction.account_code = data.get('account_code', transaction.account_code)
        transaction.amount = data['amount']
        transaction.description = data.get('description')
        transaction.project_id = data.get('project_id')

        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='CashTransaction',
            entity_id=transaction.id,
            action='UPDATE',
            old_values=old_values,
            new_values={
                'id': transaction.id,
                'project_id': transaction.project_id,
                'date': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
                'type': transaction.type,
                'category': transaction.category,
                'amount': transaction.amount,
                'description': transaction.description
            },
            entity_name=f"{transaction.type.upper()} - {transaction.category}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        response_data = {
            'id': transaction.id,
            'project_id': transaction.project_id,
            'date': transaction.date.strftime('%Y-%m-%d'),
            'type': transaction.type,
            'category': transaction.category,
            'amount': transaction.amount,
            'description': transaction.description
        }

        return success_response(response_data, "Transaction updated successfully")
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except TypeError as e:
        db.session.rollback()
        return error_response("Invalid data type in request", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update transaction error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update transaction")


# ✅ Get all transactions with optional filters
@finance_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        project_id = request.args.get('project_id')
        tx_type = request.args.get('type')
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        if page < 1 or per_page < 1:
            return error_response("Page and per_page must be positive integers", status_code=400)

        query = CashTransaction.query

        if project_id:
            query = query.filter_by(project_id=project_id)
        if tx_type:
            query = query.filter_by(type=tx_type)
        if start_date:
            query = query.filter(CashTransaction.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(CashTransaction.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

        paginated = query.order_by(CashTransaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

        items = [{
            'id': tx.id,
            'project_id': tx.project_id,
            'project_name': tx.project_name,
            'staff_id': tx.staff_id,
            'staff_name': tx.staff_name,
            'date': tx.date.strftime('%Y-%m-%d'),
            'type': tx.type,
            'category': tx.category,
            'amount': tx.amount,
            'description': tx.description
        } for tx in paginated.items]

        return paginated_response(
            items=items,
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Transactions retrieved successfully"
        )
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get transactions error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve transactions")


# ✅ Get finance summary
@finance_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    try:
        transactions = CashTransaction.query.all()
        income = sum(tx.amount for tx in transactions if tx.type == 'income')
        expense = sum(tx.amount for tx in transactions if tx.type == 'expense')
        balance = income - expense

        return success_response({
            'total_income': income,
            'total_expense': expense,
            'balance': balance
        }, "Finance summary retrieved successfully")
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get summary error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve finance summary")


# ✅ Get finance dashboard data
@finance_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get dashboard finance data including monthly revenue"""
    try:
        from datetime import date, timedelta
        from dateutil.relativedelta import relativedelta

        # Get current month
        today = date.today()
        month_start = today.replace(day=1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

        # Get this month's income
        monthly_transactions = CashTransaction.query.filter(
            CashTransaction.type == 'income',
            CashTransaction.date >= month_start,
            CashTransaction.date <= month_end
        ).all()

        monthly_revenue = sum(tx.amount for tx in monthly_transactions)

        # Get all time totals
        all_transactions = CashTransaction.query.all()
        total_income = sum(tx.amount for tx in all_transactions if tx.type == 'income')
        total_expense = sum(tx.amount for tx in all_transactions if tx.type == 'expense')
        total_balance = total_income - total_expense

        return success_response({
            'monthlyRevenue': monthly_revenue,
            'totalIncome': total_income,
            'totalExpense': total_expense,
            'totalBalance': total_balance
        }, "Finance dashboard data retrieved successfully")
    except ValueError as e:
        logger.error(f"Get dashboard error: {str(e)}", exc_info=True)
        return success_response({
            'monthlyRevenue': 0,
            'totalIncome': 0,
            'totalExpense': 0,
            'totalBalance': 0
        }, "Finance dashboard data (default)")
    except IntegrityError as e:
        logger.error(f"Get dashboard error: {str(e)}", exc_info=True)
        return success_response({
            'monthlyRevenue': 0,
            'totalIncome': 0,
            'totalExpense': 0,
            'totalBalance': 0
        }, "Finance dashboard data (default)")
    except Exception as e:
        # Return empty dashboard data on error instead of failing
        logger.error(f"Get dashboard error: {str(e)}", exc_info=True)
        return success_response({
            'monthlyRevenue': 0,
            'totalIncome': 0,
            'totalExpense': 0,
            'totalBalance': 0
        }, "Finance dashboard data (default)")


# ✅ Download dynamic reports
@finance_bp.route('/report/download', methods=['GET'])
@jwt_required()
def download_report():
    try:
        query = CashTransaction.query
        project_id = request.args.get('project_id')
        tx_type = request.args.get('type')
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        mode = request.args.get('mode', 'default')

        if project_id:
            query = query.filter_by(project_id=project_id)
        if tx_type:
            query = query.filter_by(type=tx_type)
        if start_date:
            query = query.filter(CashTransaction.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(CashTransaction.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

        transactions = query.order_by(CashTransaction.date.desc()).all()

        if mode == 'project':
            df = pd.DataFrame([t.__dict__ for t in transactions])
            df = df.groupby('project_id')['amount'].sum().reset_index()
        elif mode == 'type':
            df = pd.DataFrame([t.__dict__ for t in transactions])
            df = df.groupby('type')['amount'].sum().reset_index()
        elif mode == 'category':
            df = pd.DataFrame([t.__dict__ for t in transactions])
            df = df.groupby(['type', 'category'])['amount'].sum().reset_index()
        elif mode == 'monthly':
            df = pd.DataFrame([{
                'Month': tx.date.strftime('%Y-%m'),
                'Type': tx.type,
                'Amount': tx.amount
            } for tx in transactions])
            df = df.groupby(['Month', 'Type'])['Amount'].sum().unstack(fill_value=0).reset_index()
        elif mode == 'pl':
            income = sum(tx.amount for tx in transactions if tx.type == 'income')
            expense = sum(tx.amount for tx in transactions if tx.type == 'expense')
            df = pd.DataFrame([{
                'Total Income': income,
                'Total Expense': expense,
                'Profit/Loss': income - expense
            }])
        else:
            df = pd.DataFrame([{
                'Date': tx.date.strftime('%Y-%m-%d'),
                'Type': tx.type.title(),
                'Category': tx.category,
                'Amount': tx.amount,
                'Description': tx.description or '',
                'Project ID': tx.project_id
            } for tx in transactions])

        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='Finance_Report.xlsx',
            as_attachment=True
        )
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        logger.error(f"Download report error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to generate report")


# ✅ Delete a transaction
@finance_bp.route('/transaction/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    try:
        transaction = CashTransaction.query.get(transaction_id)
        if not transaction:
            return not_found_response("Transaction", details=f"No transaction with ID {transaction_id} found")

        # Capture data BEFORE delete
        deleted_data = {
            'id': transaction.id,
            'project_id': transaction.project_id,
            'date': transaction.date.strftime('%Y-%m-%d') if transaction.date else None,
            'type': transaction.type,
            'category': transaction.category,
            'amount': transaction.amount,
            'description': transaction.description
        }
        transaction_name = f"{transaction.type.upper()} - {transaction.category}"

        db.session.delete(transaction)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='CashTransaction',
            entity_id=transaction_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=transaction_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Transaction deleted successfully")
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete transaction error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete transaction")


# ✅ Get all projects for cost analysis
@finance_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    from project_management.models.models import Project
    from user_management.models import User

    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        # Get all projects for current user's company
        projects = Project.query.filter_by(company_id=user.company_id).all()

        return success_response([{
            'id': p.id,
            'name': p.name,
            'location': p.location,
            'status': p.status
        } for p in projects], "Projects retrieved successfully")
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get projects error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve projects")


# ✅ Get project cost analysis
@finance_bp.route('/project-cost/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_cost(project_id):
    from project_management.models.models import Project

    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        # Calculate costs from transactions for this project
        material_cost = 0
        labor_cost = 0
        vehicle_cost = 0
        revenue = 0

        transactions = CashTransaction.query.filter_by(project_id=project_id).all()

        for transaction in transactions:
            amount = float(transaction.amount or 0)
            if transaction.type == 'income':
                revenue += amount
            else:
                if 'material' in transaction.category.lower():
                    material_cost += amount
                elif 'labor' in transaction.category.lower() or 'salary' in transaction.category.lower():
                    labor_cost += amount
                elif 'vehicle' in transaction.category.lower() or 'fuel' in transaction.category.lower():
                    vehicle_cost += amount

        total_cost = material_cost + labor_cost + vehicle_cost
        profit = revenue - total_cost
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0

        # Calculate percentages
        material_percentage = (material_cost / total_cost * 100) if total_cost > 0 else 0
        labor_percentage = (labor_cost / total_cost * 100) if total_cost > 0 else 0
        vehicle_percentage = (vehicle_cost / total_cost * 100) if total_cost > 0 else 0

        return success_response({
            'project_name': project.name,
            'location': project.location,
            'status': project.status,
            'total_cost': round(total_cost, 2),
            'revenue': round(revenue, 2),
            'profit': round(profit, 2),
            'profit_margin': round(profit_margin, 2),
            'material_cost': round(material_cost, 2),
            'material_percentage': round(material_percentage, 2),
            'labor_cost': round(labor_cost, 2),
            'labor_percentage': round(labor_percentage, 2),
            'vehicle_cost': round(vehicle_cost, 2),
            'vehicle_percentage': round(vehicle_percentage, 2),
            'transaction_count': len(transactions)
        }, "Project cost analysis retrieved successfully")
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get project cost error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve project cost")


# ✅ Invoice Management
@finance_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get all invoices for the current user's company"""
    try:
        from finance_management.models.invoice import Invoice
        from user_management.models import User

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()

        return success_response([invoice.to_dict() for invoice in invoices], "Invoices retrieved successfully")

    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get invoices error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve invoices")


@finance_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create a new invoice with GST support"""
    try:
        from finance_management.models.invoice import Invoice
        from user_management.models import User
        import uuid

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        data = request.get_json(silent=True) or {}

        # Validate required fields
        errors = []
        if not data.get('customer'):
            errors.append({"field": "customer", "message": "Customer is required"})
        if data.get('subtotal') is None:
            errors.append({"field": "subtotal", "message": "Subtotal is required"})
        if not data.get('date'):
            errors.append({"field": "date", "message": "Invoice date is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Parse date
        try:
            invoice_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response("Invalid date format. Use YYYY-MM-DD", status_code=400)

        # Generate unique invoice ID
        invoice_id = f"INV-{user.company_id}-{int(datetime.now().timestamp())}"

        # Calculate amounts
        subtotal = float(data.get('subtotal', 0))
        include_gst = data.get('include_gst', True)
        gst_rate = float(data.get('gst_rate', 18)) if include_gst else 0
        gst_amount = float(data.get('gst_amount', 0))
        discount = float(data.get('discount', 0))
        total_amount = float(data.get('total_amount', subtotal + gst_amount - discount))

        # Create invoice
        invoice = Invoice(
            invoice_id=invoice_id,
            client=data.get('customer', ''),
            subtotal=subtotal,
            include_gst=include_gst,
            gst_rate=gst_rate,
            gst_amount=gst_amount,
            discount=discount,
            total=total_amount,
            due_date=invoice_date + timedelta(days=data.get('due_days', 30)),  # Default 30 days
            status='draft',
            description=data.get('description', ''),
            company_id=user.company_id if user else None
        )

        db.session.add(invoice)
        db.session.commit()

        # ✅ LOG ACTIVITY
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Invoice',
            entity_id=invoice.id,
            action='CREATE',
            new_values=invoice.to_dict(),
            entity_name=invoice.invoice_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(invoice.to_dict(), "Invoice created successfully with GST", status_code=201)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except TypeError as e:
        db.session.rollback()
        return error_response("Invalid data type in request", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create invoice error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create invoice")


@finance_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get a specific invoice"""
    try:
        from finance_management.models.invoice import Invoice
        from user_management.models import User

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        invoice = Invoice.query.get(invoice_id)

        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        return success_response(invoice.to_dict(), "Invoice retrieved successfully")

    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except TypeError as e:
        return error_response("Invalid data type in request", status_code=400)
    except Exception as e:
        logger.error(f"Get invoice error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve invoice")


@finance_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    """Update an invoice"""
    try:
        from finance_management.models.invoice import Invoice
        from user_management.models import User

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        invoice = Invoice.query.get(invoice_id)

        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        # Capture old values BEFORE update
        old_values = invoice.to_dict()

        data = request.get_json(silent=True) or {}

        # Update fields
        if 'client' in data:
            invoice.client = data['client']
        if 'total' in data:
            invoice.total = float(data['total'])
        if 'due_date' in data:
            try:
                invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response("Invalid date format. Use YYYY-MM-DD", status_code=400)
        if 'status' in data:
            invoice.status = data['status']
        if 'description' in data:
            invoice.description = data['description']

        db.session.commit()

        # ✅ LOG ACTIVITY
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Invoice',
            entity_id=invoice.id,
            action='UPDATE',
            old_values=old_values,
            new_values=invoice.to_dict(),
            entity_name=invoice.invoice_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(invoice.to_dict(), "Invoice updated successfully")

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except TypeError as e:
        db.session.rollback()
        return error_response("Invalid data type in request", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update invoice error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update invoice")


@finance_bp.route('/invoices/<int:invoice_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_id):
    """Delete an invoice"""
    try:
        from finance_management.models.invoice import Invoice
        from user_management.models import User

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        invoice = Invoice.query.get(invoice_id)

        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        # Capture data BEFORE delete
        deleted_data = invoice.to_dict()
        invoice_name = invoice.invoice_id

        db.session.delete(invoice)
        db.session.commit()

        # ✅ LOG ACTIVITY
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Invoice',
            entity_id=invoice_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=invoice_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Invoice deleted successfully")

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete invoice error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete invoice")


@finance_bp.route('/invoices/<int:invoice_id>/download', methods=['GET'])
@jwt_required()
def download_invoice(invoice_id):
    """Download invoice as PDF"""
    try:
        from finance_management.models.invoice import Invoice
        from user_management.models import User

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        invoice = Invoice.query.get(invoice_id)

        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Add title
        elements.append(Paragraph('INVOICE', title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Invoice details section
        invoice_data = [
            ['Invoice ID:', invoice.invoice_id, 'Date:', invoice.created_at.strftime('%Y-%m-%d')],
            ['Client:', invoice.client, 'Due Date:', invoice.due_date.strftime('%Y-%m-%d')],
            ['Status:', invoice.status.upper(), 'Amount:', f'${invoice.total:,.2f}']
        ]

        invoice_table = Table(invoice_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        invoice_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))

        elements.append(invoice_table)
        elements.append(Spacer(1, 0.3*inch))

        # Description section
        if invoice.description:
            elements.append(Paragraph('Description', heading_style))
            elements.append(Paragraph(invoice.description, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))

        # Summary section
        elements.append(Paragraph('Summary', heading_style))
        summary_data = [
            ['Total Amount:', f'${invoice.total:,.2f}']
        ]
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 12),
            ('FONT', (1, 0), (1, 0), 'Helvetica-Bold', 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, 0), 10),
            ('RIGHTPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*inch))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#a0aec0'),
            alignment=1
        )
        elements.append(Paragraph('Thank you for your business!', footer_style))

        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            download_name=f'invoice-{invoice.invoice_id}.pdf',
            as_attachment=True
        )

    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Download invoice error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to generate PDF")


@finance_bp.route('/invoices/<int:invoice_id>/send-email', methods=['POST'])
@jwt_required()
def send_invoice_email(invoice_id):
    """Send invoice via email"""
    try:
        from finance_management.models.invoice import Invoice
        from user_management.models import User

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return not_found_response("User", details="User not found")

        invoice = Invoice.query.get(invoice_id)

        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        # Get email from request or use invoice client email
        data = request.get_json(silent=True) or {}
        recipient_email = data.get('email', invoice.client)

        # Validate email format
        if not recipient_email or '@' not in recipient_email:
            return error_response("Invalid email address", status_code=400)

        # Email configuration (using environment variables or defaults)
        sender_email = os.getenv('SMTP_EMAIL', 'noreply@constructionapp.com')
        sender_password = os.getenv('SMTP_PASSWORD', '')
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))

        # Create email message
        message = MIMEMultipart('alternative')
        message['Subject'] = f'Invoice {invoice.invoice_id}'
        message['From'] = sender_email
        message['To'] = recipient_email

        # Create HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #667eea;">Invoice {invoice.invoice_id}</h2>
                <p>Dear {invoice.client},</p>
                <p>Please find below the details of your invoice:</p>

                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f7fafc;">
                        <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>Invoice ID:</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;">{invoice.invoice_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>Amount:</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;">${invoice.total:,.2f}</td>
                    </tr>
                    <tr style="background-color: #f7fafc;">
                        <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>Due Date:</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;">{invoice.due_date.strftime('%B %d, %Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border: 1px solid #e2e8f0;">{invoice.status.upper()}</td>
                    </tr>
                </table>

                {f'<p><strong>Description:</strong></p><p>{invoice.description}</p>' if invoice.description else ''}

                <p>If you have any questions about this invoice, please contact us.</p>
                <p>Thank you for your business!</p>

                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                <p style="color: #a0aec0; font-size: 12px;">This is an automated message. Please do not reply directly to this email.</p>
            </body>
        </html>
        """

        # Attach HTML content
        html_part = MIMEText(html_body, 'html')
        message.attach(html_part)

        # If SMTP credentials are configured, send email
        if sender_password:
            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(message)

                # Log the email as sent (optional: could update invoice status)
                return success_response({'email_sent': True}, f'Invoice sent to {recipient_email} successfully')
            except smtplib.SMTPException:
                return server_error_response(details="Failed to send email due to SMTP error")
        else:
            # No SMTP configured, return simulated success for demo purposes
            return success_response({
                'email_prepared': True,
                'message': 'Email service not configured - demo mode'
            }, f'Invoice email prepared for {recipient_email} (Email service not configured - demo mode)')

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except TypeError as e:
        db.session.rollback()
        return error_response("Invalid data type in request", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Send invoice email error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to send invoice email")