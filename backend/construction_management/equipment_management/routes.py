from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from admin_management.utils.activity_logger import log_entity_action
from .models import Equipment, EquipmentMaintenanceLog, EquipmentUsage
from user_management.models import User
from datetime import datetime

equipment_bp = Blueprint("equipment", __name__, url_prefix="/api/equipment")


# ==================== EQUIPMENT CRUD ====================

@equipment_bp.route("", methods=["GET"])
@jwt_required()
def get_equipment():
    """Get all equipment with pagination and filtering"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        condition = request.args.get('condition', '')
        is_active = request.args.get('is_active', '')

        query = Equipment.query.filter_by(company_id=company_id)

        if search:
            query = query.filter(
                db.or_(
                    Equipment.name.ilike(f'%{search}%'),
                    Equipment.equipment_code.ilike(f'%{search}%'),
                    Equipment.description.ilike(f'%{search}%')
                )
            )

        if category:
            query = query.filter_by(category=category)

        if condition:
            query = query.filter_by(condition=condition)

        if is_active in ['true', 'false']:
            query = query.filter_by(is_active=is_active == 'true')

        total = query.count()
        equipment = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in equipment.items],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@equipment_bp.route("/<int:equipment_id>", methods=["GET"])
@jwt_required()
def get_equipment_detail(equipment_id):
    """Get equipment details with maintenance and usage history"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        equipment = Equipment.query.filter_by(id=equipment_id, company_id=company_id).first()
        if not equipment:
            return jsonify({'success': False, 'error': 'Equipment not found'}), 404

        return jsonify({
            'success': True,
            'data': equipment.to_dict(include_details=True)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@equipment_bp.route("", methods=["POST"])
@jwt_required()
def create_equipment():
    """Create new equipment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        data = request.get_json()

        # Validate required fields
        if not data.get('name') or not data.get('equipment_code') or not data.get('category'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Check duplicate code
        if Equipment.query.filter_by(equipment_code=data.get('equipment_code'), company_id=company_id).first():
            return jsonify({'success': False, 'error': 'Equipment code already exists'}), 400

        equipment = Equipment(
            company_id=company_id,
            name=data.get('name'),
            category=data.get('category'),
            equipment_code=data.get('equipment_code'),
            description=data.get('description'),
            purchase_date=datetime.fromisoformat(data.get('purchase_date')) if data.get('purchase_date') else None,
            purchase_cost=float(data.get('purchase_cost', 0)),
            current_value=float(data.get('current_value', 0)),
            depreciation_rate=float(data.get('depreciation_rate', 0.1)),
            condition=data.get('condition', 'Good'),
            location=data.get('location'),
            supplier_id=data.get('supplier_id'),
            created_by=user_id,
            updated_by=user_id
        )

        db.session.add(equipment)
        db.session.commit()

        # Log activity
        log_entity_action(user_id, company_id, 'Equipment', 'CREATE', equipment.id, None, equipment.to_dict())

        return jsonify({
            'success': True,
            'message': 'Equipment created successfully',
            'data': equipment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@equipment_bp.route("/<int:equipment_id>", methods=["PUT"])
@jwt_required()
def update_equipment(equipment_id):
    """Update equipment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        equipment = Equipment.query.filter_by(id=equipment_id, company_id=company_id).first()
        if not equipment:
            return jsonify({'success': False, 'error': 'Equipment not found'}), 404

        data = request.get_json()
        old_data = equipment.to_dict()

        # Update fields
        if 'name' in data:
            equipment.name = data['name']
        if 'category' in data:
            equipment.category = data['category']
        if 'description' in data:
            equipment.description = data['description']
        if 'purchase_cost' in data:
            equipment.purchase_cost = float(data['purchase_cost'])
        if 'current_value' in data:
            equipment.current_value = float(data['current_value'])
        if 'depreciation_rate' in data:
            equipment.depreciation_rate = float(data['depreciation_rate'])
        if 'condition' in data:
            equipment.condition = data['condition']
        if 'location' in data:
            equipment.location = data['location']
        if 'is_active' in data:
            equipment.is_active = data['is_active']
        if 'supplier_id' in data:
            equipment.supplier_id = data['supplier_id']

        equipment.updated_by = user_id
        db.session.commit()

        # Log activity
        log_entity_action(user_id, company_id, 'Equipment', 'UPDATE', equipment.id, old_data, equipment.to_dict())

        return jsonify({
            'success': True,
            'message': 'Equipment updated successfully',
            'data': equipment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@equipment_bp.route("/<int:equipment_id>", methods=["DELETE"])
@jwt_required()
def delete_equipment(equipment_id):
    """Delete equipment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        equipment = Equipment.query.filter_by(id=equipment_id, company_id=company_id).first()
        if not equipment:
            return jsonify({'success': False, 'error': 'Equipment not found'}), 404

        data = equipment.to_dict()
        db.session.delete(equipment)
        db.session.commit()

        # Log activity
        log_entity_action(user_id, company_id, 'Equipment', 'DELETE', equipment.id, data, None)

        return jsonify({'success': True, 'message': 'Equipment deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MAINTENANCE LOGS ====================

@equipment_bp.route("/<int:equipment_id>/maintenance", methods=["GET"])
@jwt_required()
def get_maintenance_logs(equipment_id):
    """Get maintenance logs for equipment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        equipment = Equipment.query.filter_by(id=equipment_id, company_id=company_id).first()
        if not equipment:
            return jsonify({'success': False, 'error': 'Equipment not found'}), 404

        logs = MaintenanceLog.query.filter_by(equipment_id=equipment_id).order_by(
            MaintenanceLog.maintenance_date.desc()
        ).all()

        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@equipment_bp.route("/<int:equipment_id>/maintenance", methods=["POST"])
@jwt_required()
def add_maintenance_log(equipment_id):
    """Add maintenance log to equipment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        equipment = Equipment.query.filter_by(id=equipment_id, company_id=company_id).first()
        if not equipment:
            return jsonify({'success': False, 'error': 'Equipment not found'}), 404

        data = request.get_json()

        if not data.get('maintenance_type') or not data.get('description'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        log = MaintenanceLog(
            equipment_id=equipment_id,
            company_id=company_id,
            maintenance_date=datetime.fromisoformat(data.get('maintenance_date')) if data.get('maintenance_date') else datetime.utcnow(),
            maintenance_type=data.get('maintenance_type'),
            description=data.get('description'),
            cost=float(data.get('cost', 0)),
            next_due_date=datetime.fromisoformat(data.get('next_due_date')) if data.get('next_due_date') else None,
            performed_by=data.get('performed_by'),
            notes=data.get('notes'),
            created_by=user_id
        )

        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Maintenance log added successfully',
            'data': log.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== EQUIPMENT USAGE ====================

@equipment_bp.route("/<int:equipment_id>/usage", methods=["GET"])
@jwt_required()
def get_usage_history(equipment_id):
    """Get usage history for equipment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        equipment = Equipment.query.filter_by(id=equipment_id, company_id=company_id).first()
        if not equipment:
            return jsonify({'success': False, 'error': 'Equipment not found'}), 404

        usage = EquipmentUsage.query.filter_by(equipment_id=equipment_id).order_by(
            EquipmentUsage.assigned_date.desc()
        ).all()

        return jsonify({
            'success': True,
            'data': [u.to_dict() for u in usage]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@equipment_bp.route("/<int:equipment_id>/usage", methods=["POST"])
@jwt_required()
def record_equipment_usage(equipment_id):
    """Record equipment usage on a project"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        equipment = Equipment.query.filter_by(id=equipment_id, company_id=company_id).first()
        if not equipment:
            return jsonify({'success': False, 'error': 'Equipment not found'}), 404

        data = request.get_json()

        if not data.get('project_id'):
            return jsonify({'success': False, 'error': 'Project ID required'}), 400

        usage = EquipmentUsage(
            equipment_id=equipment_id,
            project_id=data.get('project_id'),
            company_id=company_id,
            assigned_date=datetime.fromisoformat(data.get('assigned_date')) if data.get('assigned_date') else datetime.utcnow(),
            returned_date=datetime.fromisoformat(data.get('returned_date')) if data.get('returned_date') else None,
            hours_used=float(data.get('hours_used', 0)),
            days_used=int(data.get('days_used', 0)),
            staff_id=data.get('staff_id')
        )

        db.session.add(usage)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Equipment usage recorded successfully',
            'data': usage.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@equipment_bp.route("/usage/<int:usage_id>", methods=["PUT"])
@jwt_required()
def close_equipment_usage(usage_id):
    """Record equipment return and condition"""
    try:
        user_id = get_jwt_identity()

        usage = EquipmentUsage.query.get(usage_id)
        if not usage:
            return jsonify({'success': False, 'error': 'Usage record not found'}), 404

        data = request.get_json()

        usage.returned_date = datetime.fromisoformat(data.get('returned_date')) if data.get('returned_date') else datetime.utcnow()
        usage.hours_used = float(data.get('hours_used', usage.hours_used))
        usage.condition_on_return = data.get('condition_on_return')
        usage.return_notes = data.get('return_notes')

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Equipment return recorded successfully',
            'data': usage.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== STATISTICS ====================

@equipment_bp.route("/stats", methods=["GET"])
@jwt_required()
def equipment_stats():
    """Get equipment statistics for dashboard"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        company_id = user.company_id

        total = Equipment.query.filter_by(company_id=company_id).count()
        active = Equipment.query.filter_by(company_id=company_id, is_active=True).count()
        available = Equipment.query.filter_by(company_id=company_id, condition="Good", is_active=True).count()
        under_maintenance = Equipment.query.filter_by(company_id=company_id, condition="Under Maintenance").count()
        damaged = Equipment.query.filter_by(company_id=company_id, condition="Damaged").count()

        return jsonify({
            "success": True,
            "data": {
                "total": total,
                "active": active,
                "available": available,
                "under_maintenance": under_maintenance,
                "damaged": damaged
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== HEALTH CHECK ====================

@equipment_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"module": "equipment", "status": "working"}), 200
