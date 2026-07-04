from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from supplier_management.models import Supplier
from purchase_management.models.vendor_performance import VendorPerformance
from user_management.models import User
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, paginated_response
import json

vendor_bp = Blueprint('vendor', __name__)


# ✅ Get all vendors with pagination and search
@vendor_bp.route('/vendors', methods=['GET'])
@jwt_required()
def get_vendors():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)

        query = Supplier.query

        if search:
            query = query.filter(
                db.or_(
                    Supplier.name.ilike(f'%{search}%'),
                    Supplier.email.ilike(f'%{search}%'),
                    Supplier.gstin.ilike(f'%{search}%')
                )
            )

        total = query.count()
        suppliers = query.paginate(page=page, per_page=per_page).items

        data = []
        for supplier in suppliers:
            vendor_data = supplier.to_dict() if hasattr(supplier, 'to_dict') else {
                'id': supplier.id,
                'name': supplier.name,
                'email': supplier.email,
                'phone': supplier.phone if hasattr(supplier, 'phone') else None,
                'location': supplier.location if hasattr(supplier, 'location') else None,
                'gstin': supplier.gstin if hasattr(supplier, 'gstin') else None,
            }

            # Add performance score
            latest_performance = VendorPerformance.query.filter_by(vendor_id=supplier.id).order_by(
                VendorPerformance.recorded_date.desc()
            ).first()

            vendor_data['performance_score'] = latest_performance.overall_score if latest_performance else 0

            data.append(vendor_data)

        return paginated_response(
            data,
            page,
            per_page,
            total,
            "Vendors retrieved",
            status_code=200
        )
    except Exception as e:
        return error_response(f"Error fetching vendors: {str(e)}", status_code=500)


# ✅ Get single vendor details
@vendor_bp.route('/vendors/<int:vendor_id>', methods=['GET'])
@jwt_required()
def get_vendor(vendor_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        vendor = Supplier.query.get(vendor_id)
        if not vendor:
            return error_response("Vendor not found", status_code=404)

        vendor_data = vendor.to_dict() if hasattr(vendor, 'to_dict') else {
            'id': vendor.id,
            'name': vendor.name,
            'email': vendor.email,
            'phone': vendor.phone if hasattr(vendor, 'phone') else None,
            'location': vendor.location if hasattr(vendor, 'location') else None,
            'gstin': vendor.gstin if hasattr(vendor, 'gstin') else None,
        }

        # Add enhanced vendor fields if they exist
        if hasattr(vendor, 'bank_name'):
            vendor_data['bank_name'] = vendor.bank_name
        if hasattr(vendor, 'account_number'):
            vendor_data['account_number'] = vendor.account_number
        if hasattr(vendor, 'ifsc_code'):
            vendor_data['ifsc_code'] = vendor.ifsc_code
        if hasattr(vendor, 'pan'):
            vendor_data['pan'] = vendor.pan
        if hasattr(vendor, 'payment_terms'):
            vendor_data['payment_terms'] = vendor.payment_terms
        if hasattr(vendor, 'credit_limit'):
            vendor_data['credit_limit'] = vendor.credit_limit
        if hasattr(vendor, 'contact_persons'):
            vendor_data['contact_persons'] = vendor.contact_persons

        # Add performance records
        performance_records = VendorPerformance.query.filter_by(vendor_id=vendor_id).order_by(
            VendorPerformance.recorded_date.desc()
        ).limit(10).all()

        vendor_data['performance_history'] = [perf.to_dict() for perf in performance_records]

        # Calculate current performance score
        if performance_records:
            vendor_data['current_performance_score'] = performance_records[0].overall_score
        else:
            vendor_data['current_performance_score'] = 0

        return success_response(vendor_data, "Vendor retrieved", status_code=200)
    except Exception as e:
        return error_response(f"Error fetching vendor: {str(e)}", status_code=500)


# ✅ Create/Update vendor
@vendor_bp.route('/vendors', methods=['POST'])
@jwt_required()
def create_vendor():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        # Validation
        errors = []
        if not data.get('name'):
            errors.append({"field": "name", "message": "Vendor name is required"})
        if not data.get('email'):
            errors.append({"field": "email", "message": "Email is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Create vendor
        vendor = Supplier(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            location=data.get('location'),
            gstin=data.get('gstin'),
            pan=data.get('pan'),
            bank_name=data.get('bank_name'),
            account_number=data.get('account_number'),
            ifsc_code=data.get('ifsc_code'),
            payment_terms=data.get('payment_terms', '30days'),
            credit_limit=data.get('credit_limit', 0),
            contact_persons=json.dumps(data.get('contact_persons', [])) if data.get('contact_persons') else '[]',
        )

        db.session.add(vendor)
        db.session.commit()

        log_entity_action(user_id, 'Supplier', vendor.id, 'CREATE', f"Created vendor: {vendor.name}")

        vendor_data = {
            'id': vendor.id,
            'name': vendor.name,
            'email': vendor.email,
            'phone': vendor.phone,
            'location': vendor.location,
            'gstin': vendor.gstin,
            'pan': vendor.pan,
            'bank_name': vendor.bank_name,
            'account_number': vendor.account_number,
            'ifsc_code': vendor.ifsc_code,
            'payment_terms': vendor.payment_terms,
            'credit_limit': vendor.credit_limit,
            'contact_persons': json.loads(vendor.contact_persons) if vendor.contact_persons else [],
            'performance_score': 0,
        }

        return success_response(vendor_data, "Vendor created successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating vendor: {str(e)}", status_code=500)


# ✅ Update vendor
@vendor_bp.route('/vendors/<int:vendor_id>', methods=['PUT'])
@jwt_required()
def update_vendor(vendor_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        vendor = Supplier.query.get(vendor_id)
        if not vendor:
            return error_response("Vendor not found", status_code=404)

        # Update fields
        if data.get('name'):
            vendor.name = data.get('name')
        if data.get('email'):
            vendor.email = data.get('email')
        if data.get('phone'):
            vendor.phone = data.get('phone')
        if data.get('location'):
            vendor.location = data.get('location')
        if data.get('gstin'):
            vendor.gstin = data.get('gstin')
        if data.get('pan'):
            vendor.pan = data.get('pan')
        if data.get('bank_name'):
            vendor.bank_name = data.get('bank_name')
        if data.get('account_number'):
            vendor.account_number = data.get('account_number')
        if data.get('ifsc_code'):
            vendor.ifsc_code = data.get('ifsc_code')
        if data.get('payment_terms'):
            vendor.payment_terms = data.get('payment_terms')
        if data.get('credit_limit') is not None:
            vendor.credit_limit = data.get('credit_limit')
        if data.get('contact_persons') is not None:
            vendor.contact_persons = json.dumps(data.get('contact_persons'))

        db.session.commit()

        log_entity_action(user_id, 'Supplier', vendor.id, 'UPDATE', f"Updated vendor: {vendor.name}")

        vendor_data = {
            'id': vendor.id,
            'name': vendor.name,
            'email': vendor.email,
            'phone': vendor.phone,
            'location': vendor.location,
            'gstin': vendor.gstin,
            'pan': vendor.pan,
            'bank_name': vendor.bank_name,
            'account_number': vendor.account_number,
            'ifsc_code': vendor.ifsc_code,
            'payment_terms': vendor.payment_terms,
            'credit_limit': vendor.credit_limit,
            'contact_persons': json.loads(vendor.contact_persons) if vendor.contact_persons else [],
        }

        return success_response(vendor_data, "Vendor updated successfully", status_code=200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating vendor: {str(e)}", status_code=500)


# ✅ Record vendor performance
@vendor_bp.route('/vendors/<int:vendor_id>/performance', methods=['POST'])
@jwt_required()
def record_vendor_performance(vendor_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        vendor = Supplier.query.get(vendor_id)
        if not vendor:
            return error_response("Vendor not found", status_code=404)

        # Validation
        errors = []
        if data.get('on_time_percentage') is None:
            errors.append({"field": "on_time_percentage", "message": "On-time percentage is required"})
        if data.get('quality_score') is None:
            errors.append({"field": "quality_score", "message": "Quality score is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Create performance record
        performance = VendorPerformance(
            vendor_id=vendor_id,
            on_time_percentage=float(data.get('on_time_percentage')),
            quality_score=float(data.get('quality_score')),
            notes=data.get('notes'),
            created_by_id=user_id
        )

        performance.calculate_overall_score()

        db.session.add(performance)
        db.session.commit()

        log_entity_action(user_id, 'VendorPerformance', performance.id, 'CREATE', f"Recorded performance for vendor: {vendor.name}")

        return success_response(performance.to_dict(), "Performance recorded successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error recording performance: {str(e)}", status_code=500)


# ✅ Get vendor performance history
@vendor_bp.route('/vendors/<int:vendor_id>/performance', methods=['GET'])
@jwt_required()
def get_vendor_performance(vendor_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        vendor = Supplier.query.get(vendor_id)
        if not vendor:
            return error_response("Vendor not found", status_code=404)

        query = VendorPerformance.query.filter_by(vendor_id=vendor_id).order_by(VendorPerformance.recorded_date.desc())

        total = query.count()
        records = query.paginate(page=page, per_page=per_page).items

        data = [record.to_dict() for record in records]

        # Calculate average scores
        all_records = VendorPerformance.query.filter_by(vendor_id=vendor_id).all()
        avg_on_time = sum(r.on_time_percentage for r in all_records) / len(all_records) if all_records else 0
        avg_quality = sum(r.quality_score for r in all_records) / len(all_records) if all_records else 0
        avg_overall = sum(r.overall_score for r in all_records) / len(all_records) if all_records else 0

        result = {
            'vendor_id': vendor_id,
            'vendor_name': vendor.name,
            'total_records': total,
            'average_on_time_percentage': avg_on_time,
            'average_quality_score': avg_quality,
            'average_overall_score': avg_overall,
            'records': data,
        }

        return paginated_response(
            result,
            page,
            per_page,
            total,
            "Vendor performance retrieved",
            status_code=200
        )
    except Exception as e:
        return error_response(f"Error fetching performance: {str(e)}", status_code=500)
