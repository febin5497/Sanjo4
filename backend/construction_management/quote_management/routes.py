from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from admin_management.utils.activity_logger import log_entity_action
from .models import Quote, QuoteItem, QuoteTemplate, TemplateItem
from .pdf_service import generate_quote_pdf, generate_quote_csv
from user_management.models import User
from project_management.models.models import Project
from client_management.models import Client
from datetime import datetime, timedelta
from sqlalchemy import and_
from io import BytesIO

quote_bp = Blueprint("quotes", __name__, url_prefix="/api/quotes")


# ==================== QUOTE CRUD ====================

@quote_bp.route("", methods=["GET"])
@jwt_required()
def get_quotes():
    """Get all quotes with pagination and filtering"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        client_id = request.args.get('client_id', '', type=int)

        query = Quote.query.filter_by(company_id=company_id)

        if search:
            query = query.filter(
                db.or_(
                    Quote.quote_number.ilike(f'%{search}%'),
                    Client.name.ilike(f'%{search}%')
                )
            ).join(Client)

        if status:
            query = query.filter_by(status=status)

        if client_id:
            query = query.filter_by(client_id=client_id)

        total = query.count()
        quotes = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'success': True,
            'data': [q.to_dict() for q in quotes.items],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/<int:quote_id>", methods=["GET"])
@jwt_required()
def get_quote_detail(quote_id):
    """Get quote details with line items"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        quote = Quote.query.filter_by(id=quote_id, company_id=company_id).first()
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404

        return jsonify({
            'success': True,
            'data': quote.to_dict(include_items=True)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("", methods=["POST"])
@jwt_required()
def create_quote():
    """Create new quote"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        data = request.get_json()

        # Validate required fields
        if not data.get('quote_number') or not data.get('client_id'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Check duplicate quote number
        if Quote.query.filter_by(quote_number=data.get('quote_number'), company_id=company_id).first():
            return jsonify({'success': False, 'error': 'Quote number already exists'}), 400

        quote = Quote(
            company_id=company_id,
            quote_number=data.get('quote_number'),
            client_id=data.get('client_id'),
            supplier_id=data.get('supplier_id'),
            user_id=user_id,
            project_id=data.get('project_id'),
            tax_rate=float(data.get('tax_rate', 0)),
            status=data.get('status', 'Draft'),
            notes=data.get('notes'),
            terms_and_conditions=data.get('terms_and_conditions'),
            sent_date=datetime.fromisoformat(data.get('sent_date')) if data.get('sent_date') else None,
            valid_until=datetime.fromisoformat(data.get('valid_until')) if data.get('valid_until') else None
        )

        # Add quote items if provided
        if 'items' in data:
            for item_data in data.get('items', []):
                item = QuoteItem(
                    material_id=item_data.get('material_id'),
                    description=item_data.get('description'),
                    quantity=float(item_data.get('quantity', 1)),
                    unit_of_measure=item_data.get('unit_of_measure', 'Unit'),
                    unit_price=float(item_data.get('unit_price', 0))
                )
                item.calculate_total()
                quote.items.append(item)

        quote.calculate_totals()
        db.session.add(quote)
        db.session.commit()

        # Log activity
        log_entity_action(user_id, company_id, 'Quote', 'CREATE', quote.id, None, quote.to_dict())

        return jsonify({
            'success': True,
            'message': 'Quote created successfully',
            'data': quote.to_dict(include_items=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/<int:quote_id>", methods=["PUT"])
@jwt_required()
def update_quote(quote_id):
    """Update quote"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        quote = Quote.query.filter_by(id=quote_id, company_id=company_id).first()
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404

        data = request.get_json()
        old_data = quote.to_dict(include_items=True)

        # Update fields
        if 'quote_number' in data:
            if Quote.query.filter(
                and_(
                    Quote.quote_number == data['quote_number'],
                    Quote.company_id == company_id,
                    Quote.id != quote_id
                )
            ).first():
                return jsonify({'success': False, 'error': 'Quote number already exists'}), 400
            quote.quote_number = data['quote_number']

        if 'client_id' in data:
            quote.client_id = data['client_id']
        if 'supplier_id' in data:
            quote.supplier_id = data['supplier_id']
        if 'project_id' in data:
            quote.project_id = data['project_id']
        if 'tax_rate' in data:
            quote.tax_rate = float(data['tax_rate'])
        if 'status' in data:
            quote.status = data['status']
        if 'notes' in data:
            quote.notes = data['notes']
        if 'terms_and_conditions' in data:
            quote.terms_and_conditions = data['terms_and_conditions']
        if 'sent_date' in data:
            quote.sent_date = datetime.fromisoformat(data['sent_date']) if data['sent_date'] else None
        if 'valid_until' in data:
            quote.valid_until = datetime.fromisoformat(data['valid_until']) if data['valid_until'] else None

        # Update items if provided
        if 'items' in data:
            QuoteItem.query.filter_by(quote_id=quote_id).delete()
            for item_data in data.get('items', []):
                item = QuoteItem(
                    quote_id=quote_id,
                    material_id=item_data.get('material_id'),
                    description=item_data.get('description'),
                    quantity=float(item_data.get('quantity', 1)),
                    unit_of_measure=item_data.get('unit_of_measure', 'Unit'),
                    unit_price=float(item_data.get('unit_price', 0))
                )
                item.calculate_total()
                quote.items.append(item)

        quote.calculate_totals()
        db.session.commit()

        # Log activity
        log_entity_action(user_id, company_id, 'Quote', 'UPDATE', quote.id, old_data, quote.to_dict(include_items=True))

        return jsonify({
            'success': True,
            'message': 'Quote updated successfully',
            'data': quote.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/<int:quote_id>", methods=["DELETE"])
@jwt_required()
def delete_quote(quote_id):
    """Delete quote"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        quote = Quote.query.filter_by(id=quote_id, company_id=company_id).first()
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404

        data = quote.to_dict(include_items=True)
        db.session.delete(quote)
        db.session.commit()

        # Log activity
        log_entity_action(user_id, company_id, 'Quote', 'DELETE', quote_id, data, None)

        return jsonify({'success': True, 'message': 'Quote deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== QUOTE ITEMS ====================

@quote_bp.route("/<int:quote_id>/items", methods=["POST"])
@jwt_required()
def add_quote_item(quote_id):
    """Add item to quote"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        quote = Quote.query.filter_by(id=quote_id, company_id=company_id).first()
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404

        data = request.get_json()

        if not data.get('description'):
            return jsonify({'success': False, 'error': 'Description required'}), 400

        item = QuoteItem(
            quote_id=quote_id,
            material_id=data.get('material_id'),
            description=data.get('description'),
            quantity=float(data.get('quantity', 1)),
            unit_of_measure=data.get('unit_of_measure', 'Unit'),
            unit_price=float(data.get('unit_price', 0))
        )
        item.calculate_total()

        db.session.add(item)
        quote.calculate_totals()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Item added successfully',
            'data': item.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/items/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_quote_item(item_id):
    """Update quote item"""
    try:
        user_id = get_jwt_identity()
        item = QuoteItem.query.get(item_id)

        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        quote = item.quote
        user = User.query.get(user_id)
        if quote.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        data = request.get_json()

        if 'description' in data:
            item.description = data['description']
        if 'quantity' in data:
            item.quantity = float(data['quantity'])
        if 'unit_price' in data:
            item.unit_price = float(data['unit_price'])
        if 'unit_of_measure' in data:
            item.unit_of_measure = data['unit_of_measure']
        if 'material_id' in data:
            item.material_id = data['material_id']

        item.calculate_total()
        quote.calculate_totals()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Item updated successfully',
            'data': item.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_quote_item(item_id):
    """Delete quote item"""
    try:
        user_id = get_jwt_identity()
        item = QuoteItem.query.get(item_id)

        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        quote = item.quote
        user = User.query.get(user_id)
        if quote.company_id != user.company_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        db.session.delete(item)
        quote.calculate_totals()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Item deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== QUOTE STATUS & ACTIONS ====================

@quote_bp.route("/<int:quote_id>/status", methods=["PUT"])
@jwt_required()
def update_quote_status(quote_id):
    """Update quote status"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        quote = Quote.query.filter_by(id=quote_id, company_id=company_id).first()
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404

        data = request.get_json()
        new_status = data.get('status')

        valid_statuses = ['Draft', 'Sent', 'Accepted', 'Rejected', 'Expired', 'Converted']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400

        old_status = quote.status
        quote.status = new_status

        if new_status == 'Sent':
            quote.sent_date = datetime.utcnow()

        db.session.commit()

        log_entity_action(user_id, company_id, 'Quote', 'UPDATE_STATUS', quote.id,
                         {'status': old_status}, {'status': new_status})

        return jsonify({
            'success': True,
            'message': f'Quote status updated to {new_status}',
            'data': quote.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/<int:quote_id>/convert-to-project", methods=["POST"])
@jwt_required()
def convert_quote_to_project(quote_id):
    """Convert accepted quote to project"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        quote = Quote.query.filter_by(id=quote_id, company_id=company_id).first()
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404

        if quote.status != 'Accepted':
            return jsonify({'success': False, 'error': 'Only accepted quotes can be converted'}), 400

        data = request.get_json()

        # Create new project from quote
        project = Project(
            company_id=company_id,
            project_name=data.get('project_name', f"Project from Quote {quote.quote_number}"),
            description=f"Converted from Quote {quote.quote_number}",
            client_id=quote.client_id,
            project_status='Planning',
            budget=quote.total,
            created_by=user_id,
            updated_by=user_id
        )

        quote.status = 'Converted'
        quote.project_id = None  # Will be set after project creation

        db.session.add(project)
        db.session.flush()  # Get project ID without committing

        quote.project_id = project.id
        db.session.commit()

        log_entity_action(user_id, company_id, 'Quote', 'CONVERT_TO_PROJECT', quote.id,
                         {'status': 'Accepted'}, {'status': 'Converted', 'project_id': project.id})

        return jsonify({
            'success': True,
            'message': 'Quote converted to project successfully',
            'data': {
                'quote': quote.to_dict(),
                'project': project.to_dict() if hasattr(project, 'to_dict') else {'id': project.id}
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== QUOTE TEMPLATES ====================

@quote_bp.route("/templates", methods=["GET"])
@jwt_required()
def get_templates():
    """Get all quote templates"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        templates = QuoteTemplate.query.filter_by(company_id=company_id).all()

        return jsonify({
            'success': True,
            'data': [t.to_dict(include_items=True) for t in templates]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/templates", methods=["POST"])
@jwt_required()
def create_template():
    """Create new quote template"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        data = request.get_json()

        if not data.get('template_name'):
            return jsonify({'success': False, 'error': 'Template name required'}), 400

        template = QuoteTemplate(
            company_id=company_id,
            user_id=user_id,
            template_name=data.get('template_name'),
            description=data.get('description'),
            is_default=data.get('is_default', False),
            notes=data.get('notes'),
            terms_and_conditions=data.get('terms_and_conditions'),
            tax_rate=float(data.get('tax_rate', 0))
        )

        # Add template items if provided
        if 'items' in data:
            for item_data in data.get('items', []):
                item = TemplateItem(
                    material_id=item_data.get('material_id'),
                    description=item_data.get('description'),
                    quantity_default=float(item_data.get('quantity_default', 1)),
                    unit_of_measure=item_data.get('unit_of_measure', 'Unit'),
                    unit_price=float(item_data.get('unit_price', 0))
                )
                template.items.append(item)

        db.session.add(template)
        db.session.commit()

        log_entity_action(user_id, company_id, 'QuoteTemplate', 'CREATE', template.id, None, template.to_dict())

        return jsonify({
            'success': True,
            'message': 'Template created successfully',
            'data': template.to_dict(include_items=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/templates/<int:template_id>", methods=["PUT"])
@jwt_required()
def update_template(template_id):
    """Update quote template"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        template = QuoteTemplate.query.filter_by(id=template_id, company_id=company_id).first()
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404

        data = request.get_json()
        old_data = template.to_dict(include_items=True)

        if 'template_name' in data:
            template.template_name = data['template_name']
        if 'description' in data:
            template.description = data['description']
        if 'is_default' in data:
            template.is_default = data['is_default']
        if 'notes' in data:
            template.notes = data['notes']
        if 'terms_and_conditions' in data:
            template.terms_and_conditions = data['terms_and_conditions']
        if 'tax_rate' in data:
            template.tax_rate = float(data['tax_rate'])

        # Update items if provided
        if 'items' in data:
            TemplateItem.query.filter_by(template_id=template_id).delete()
            for item_data in data.get('items', []):
                item = TemplateItem(
                    template_id=template_id,
                    material_id=item_data.get('material_id'),
                    description=item_data.get('description'),
                    quantity_default=float(item_data.get('quantity_default', 1)),
                    unit_of_measure=item_data.get('unit_of_measure', 'Unit'),
                    unit_price=float(item_data.get('unit_price', 0))
                )
                template.items.append(item)

        db.session.commit()

        log_entity_action(user_id, company_id, 'QuoteTemplate', 'UPDATE', template.id, old_data, template.to_dict(include_items=True))

        return jsonify({
            'success': True,
            'message': 'Template updated successfully',
            'data': template.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/templates/<int:template_id>", methods=["DELETE"])
@jwt_required()
def delete_template(template_id):
    """Delete quote template"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        template = QuoteTemplate.query.filter_by(id=template_id, company_id=company_id).first()
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404

        data = template.to_dict(include_items=True)
        db.session.delete(template)
        db.session.commit()

        log_entity_action(user_id, company_id, 'QuoteTemplate', 'DELETE', template_id, data, None)

        return jsonify({'success': True, 'message': 'Template deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/templates/<int:template_id>/use", methods=["POST"])
@jwt_required()
def create_quote_from_template(template_id):
    """Create quote from template"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        template = QuoteTemplate.query.filter_by(id=template_id, company_id=company_id).first()
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404

        data = request.get_json()

        if not data.get('quote_number') or not data.get('client_id'):
            return jsonify({'success': False, 'error': 'Quote number and client ID required'}), 400

        # Create quote from template
        quote = Quote(
            company_id=company_id,
            quote_number=data.get('quote_number'),
            client_id=data.get('client_id'),
            supplier_id=data.get('supplier_id'),
            user_id=user_id,
            project_id=data.get('project_id'),
            tax_rate=template.tax_rate,
            status='Draft',
            notes=template.notes,
            terms_and_conditions=template.terms_and_conditions
        )

        # Add items from template
        for template_item in template.items:
            item = QuoteItem(
                material_id=template_item.material_id,
                description=template_item.description,
                quantity=template_item.quantity_default,
                unit_of_measure=template_item.unit_of_measure,
                unit_price=template_item.unit_price
            )
            item.calculate_total()
            quote.items.append(item)

        quote.calculate_totals()
        db.session.add(quote)
        db.session.commit()

        log_entity_action(user_id, company_id, 'Quote', 'CREATE_FROM_TEMPLATE', quote.id,
                         {'template_id': template_id}, quote.to_dict())

        return jsonify({
            'success': True,
            'message': 'Quote created from template successfully',
            'data': quote.to_dict(include_items=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== EXPORT ====================

@quote_bp.route("/<int:quote_id>/pdf", methods=["GET"])
@jwt_required()
def export_quote_pdf(quote_id):
    """Export quote as PDF"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        quote = Quote.query.filter_by(id=quote_id, company_id=company_id).first()
        if not quote:
            return jsonify({'success': False, 'error': 'Quote not found'}), 404

        pdf_buffer = generate_quote_pdf(quote)
        filename = f"Quote_{quote.quote_number}.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@quote_bp.route("/export/csv", methods=["POST"])
@jwt_required()
def export_quotes_csv():
    """Export quotes as CSV"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        data = request.get_json()
        quote_ids = data.get('quote_ids', [])

        if quote_ids:
            quotes = Quote.query.filter(
                Quote.id.in_(quote_ids),
                Quote.company_id == company_id
            ).all()
        else:
            quotes = Quote.query.filter_by(company_id=company_id).all()

        csv_data = generate_quote_csv(quotes)
        buffer = BytesIO(csv_data.encode())

        return send_file(
            buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name='quotes_export.csv'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@quote_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"module": "quotes", "status": "working"}), 200
