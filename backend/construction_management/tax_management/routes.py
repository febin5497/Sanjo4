"""Tax Management Routes for Indian Tax Compliance"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from utils.response_formatter import success_response, error_response, paginated_response
from tax_management.hsn_sac_codes import HSNCode, SACCode, GSTConfiguration
from tax_management.tds_module import TDSConfiguration, TDSPayment
from tax_management.professional_tax import ProfessionalTaxConfiguration, ProfessionalTaxDeduction
from tax_management.gst_reports import GSTReportService
from user_management.models import User

tax_bp = Blueprint('tax', __name__, url_prefix='/api/tax')


# ============= GST Configuration Routes =============

@tax_bp.route('/gst-config', methods=['POST'])
@jwt_required()
def create_gst_config():
    """Create/Update GST configuration for company"""
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return error_response("User not found", status_code=401)

        # Check if config already exists
        existing = GSTConfiguration.query.filter_by(company_id=user.company_id).first()

        if existing:
            existing.gstin = data.get('gstin')
            existing.company_name = data.get('company_name')
            existing.state_code = data.get('state_code')
            existing.registration_type = data.get('registration_type')
        else:
            existing = GSTConfiguration(
                company_id=user.company_id,
                gstin=data.get('gstin'),
                company_name=data.get('company_name'),
                state_code=data.get('state_code'),
                registration_type=data.get('registration_type'),
                gst_effective_date=data.get('gst_effective_date')
            )
            db.session.add(existing)

        db.session.commit()
        return success_response(existing.to_dict(), "GST configuration saved", status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), status_code=500)


@tax_bp.route('/gst-config', methods=['GET'])
@jwt_required()
def get_gst_config():
    """Get company's GST configuration"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        config = GSTConfiguration.query.filter_by(company_id=user.company_id).first()
        if not config:
            return error_response("GST configuration not found", status_code=404)

        return success_response(config.to_dict(), "GST configuration retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)


# ============= HSN Code Routes =============

@tax_bp.route('/hsn-codes', methods=['GET'])
@jwt_required()
def get_hsn_codes():
    """Get all HSN codes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)

        query = HSNCode.query
        if search:
            query = query.filter(
                (HSNCode.code.ilike(f'%{search}%')) |
                (HSNCode.description.ilike(f'%{search}%'))
            )

        paginated = query.paginate(page=page, per_page=per_page)
        return paginated_response(
            [item.to_dict() for item in paginated.items],
            paginated.total,
            page,
            per_page,
            "HSN codes retrieved"
        )
    except Exception as e:
        return error_response(str(e), status_code=500)


@tax_bp.route('/hsn-codes/<code>', methods=['GET'])
@jwt_required()
def get_hsn_code(code):
    """Get specific HSN code"""
    try:
        hsn = HSNCode.query.filter_by(code=code).first()
        if not hsn:
            return error_response("HSN code not found", status_code=404)
        return success_response(hsn.to_dict())
    except Exception as e:
        return error_response(str(e), status_code=500)


# ============= SAC Code Routes =============

@tax_bp.route('/sac-codes', methods=['GET'])
@jwt_required()
def get_sac_codes():
    """Get all SAC codes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)

        query = SACCode.query
        if search:
            query = query.filter(
                (SACCode.code.ilike(f'%{search}%')) |
                (SACCode.description.ilike(f'%{search}%'))
            )

        paginated = query.paginate(page=page, per_page=per_page)
        return paginated_response(
            [item.to_dict() for item in paginated.items],
            paginated.total,
            page,
            per_page,
            "SAC codes retrieved"
        )
    except Exception as e:
        return error_response(str(e), status_code=500)


# ============= TDS Routes =============

@tax_bp.route('/tds-config', methods=['GET'])
@jwt_required()
def get_tds_config():
    """Get TDS configuration for company"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        configs = TDSConfiguration.query.filter_by(company_id=user.company_id).all()
        return success_response([c.to_dict() for c in configs], "TDS configuration retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)


@tax_bp.route('/tds-payments', methods=['GET'])
@jwt_required()
def get_tds_payments():
    """Get TDS payments for company"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = TDSPayment.query.filter_by(company_id=user.company_id)
        paginated = query.paginate(page=page, per_page=per_page)

        return paginated_response(
            [item.to_dict() for item in paginated.items],
            paginated.total,
            page,
            per_page,
            "TDS payments retrieved"
        )
    except Exception as e:
        return error_response(str(e), status_code=500)


# ============= Professional Tax Routes =============

@tax_bp.route('/professional-tax-config', methods=['GET'])
@jwt_required()
def get_professional_tax_config():
    """Get professional tax configuration by state"""
    try:
        state = request.args.get('state', '', type=str)
        query = ProfessionalTaxConfiguration.query.filter_by(is_active=True)

        if state:
            query = query.filter_by(state=state)

        configs = query.all()
        return success_response([c.to_dict() for c in configs], "Professional tax config retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)


@tax_bp.route('/professional-tax-deductions', methods=['GET'])
@jwt_required()
def get_professional_tax_deductions():
    """Get professional tax deductions for staff"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        staff_id = request.args.get('staff_id', type=int)
        year = request.args.get('year', type=int)

        query = ProfessionalTaxDeduction.query.filter_by(company_id=user.company_id)
        if staff_id:
            query = query.filter_by(staff_id=staff_id)
        if year:
            query = query.filter_by(year=year)

        deductions = query.all()
        return success_response([d.to_dict() for d in deductions], "Professional tax deductions retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)


# ============= GST Reports Routes =============

@tax_bp.route('/reports/gst-summary', methods=['GET'])
@jwt_required()
def get_gst_summary():
    """Get monthly GST summary (Tax collected vs paid)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if not month or not year:
            return error_response("Month and year are required", status_code=400)

        summary = GSTReportService.get_monthly_gst_summary(user.company_id, month, year)
        return success_response(summary, "GST summary generated")
    except Exception as e:
        return error_response(str(e), status_code=500)


@tax_bp.route('/reports/gst-liability', methods=['GET'])
@jwt_required()
def get_gst_liability():
    """Get GST liability (Tax payable or refundable)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if not month or not year:
            return error_response("Month and year are required", status_code=400)

        liability = GSTReportService.get_gst_liability_summary(user.company_id, month, year)
        return success_response(liability, "GST liability calculated")
    except Exception as e:
        return error_response(str(e), status_code=500)


@tax_bp.route('/reports/gstr-3b', methods=['GET'])
@jwt_required()
def get_gstr3b():
    """Get GSTR-3B (Monthly return) summary"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if not month or not year:
            return error_response("Month and year are required", status_code=400)

        summary = GSTReportService.generate_gstr3b_summary(user.company_id, month, year)
        return success_response(summary, "GSTR-3B summary generated")
    except Exception as e:
        return error_response(str(e), status_code=500)


@tax_bp.route('/reports/hsn-summary', methods=['GET'])
@jwt_required()
def get_hsn_summary():
    """Get HSN-wise sales summary"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if not month or not year:
            return error_response("Month and year are required", status_code=400)

        summary = GSTReportService.get_hsn_wise_summary(user.company_id, month, year)
        return success_response(summary, "HSN-wise summary generated")
    except Exception as e:
        return error_response(str(e), status_code=500)


@tax_bp.route('/reports/customer-summary', methods=['GET'])
@jwt_required()
def get_customer_summary():
    """Get customer-wise (B2B) sales summary"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if not month or not year:
            return error_response("Month and year are required", status_code=400)

        summary = GSTReportService.get_customer_wise_summary(user.company_id, month, year)
        return success_response(summary, "Customer-wise summary generated")
    except Exception as e:
        return error_response(str(e), status_code=500)


# ============= Health Check =============

@tax_bp.route('/health', methods=['GET'])
def tax_health():
    """Health check for tax module"""
    return success_response({'status': 'operational'}, "Tax module is operational")
