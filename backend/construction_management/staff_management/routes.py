
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, bcrypt
from staff_management.models import Staff
from staff_management.expense_model import Expense
from staff_management.user_id_service import UserIDGenerator
from staff_management.user_creation_service import UserCreationService
from user_management.models import User
from datetime import datetime
from utils.response_formatter import (
    success_response, error_response, paginated_response,
    server_error_response, not_found_response
)
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")
staff_bp.strict_slashes = False


# ============================================
# VALIDATION HELPERS
# ============================================
def validate_staff_data(data):
    """Validate staff input data"""
    errors = []
    
    if not data.get('name') or len(data.get('name', '').strip()) == 0:
        errors.append("Name is required")
    elif len(data['name']) > 100:
        errors.append("Name must be less than 100 characters")
    
    if not data.get('role') or len(data.get('role', '').strip()) == 0:
        errors.append("Role is required")
    elif len(data['role']) > 100:
        errors.append("Role must be less than 100 characters")
    
    # Accept either 'phone' or 'personal_phone'
    phone = data.get('personal_phone') or data.get('phone', '')
    if not phone or len(phone.strip()) == 0:
        errors.append("Phone is required")
    elif len(phone) > 20:
        errors.append("Phone must be less than 20 characters")
    
    if data.get('email') and len(data['email']) > 100:
        errors.append("Email must be less than 100 characters")
    
    if not data.get('joining_date'):
        errors.append("Joining date is required")
    else:
        try:
            datetime.strptime(data['joining_date'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD")
    
    if 'salary' not in data or data['salary'] is None:
        errors.append("Salary is required")
    else:
        try:
            float(data['salary'])
            if float(data['salary']) < 0:
                errors.append("Salary cannot be negative")
        except (ValueError, TypeError):
            errors.append("Salary must be a valid number")
    
    if 'pf' not in data or data['pf'] is None:
        errors.append("PF is required")
    else:
        try:
            float(data['pf'])
            if not (0 <= float(data['pf']) <= 100):
                errors.append("PF must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("PF must be a valid percentage")
    
    if 'esi' not in data or data['esi'] is None:
        errors.append("ESI is required")
    else:
        try:
            float(data['esi'])
            if not (0 <= float(data['esi']) <= 100):
                errors.append("ESI must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("ESI must be a valid percentage")
    
    return errors


def validate_formal_staff_data(data):
    """Validate formal staff registration data"""
    errors = []

    # Personal Information
    if not data.get('first_name') or len(data.get('first_name', '').strip()) == 0:
        errors.append("First name is required")
    elif len(data['first_name']) > 100:
        errors.append("First name must be less than 100 characters")

    if not data.get('last_name') or len(data.get('last_name', '').strip()) == 0:
        errors.append("Last name is required")
    elif len(data['last_name']) > 100:
        errors.append("Last name must be less than 100 characters")

    if data.get('date_of_birth'):
        try:
            datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date of birth format. Use YYYY-MM-DD")

    if data.get('gender') and data['gender'] not in ['Male', 'Female', 'Other', 'male', 'female', 'other']:
        errors.append("Gender must be Male, Female, or Other")

    # Contact Information
    if not data.get('personal_phone') or len(data.get('personal_phone', '').strip()) == 0:
        errors.append("Personal phone is required")
    elif len(data['personal_phone']) > 20:
        errors.append("Phone must be less than 20 characters")

    if data.get('personal_email'):
        if '@' not in data['personal_email']:
            errors.append("Invalid email format")
        elif len(data['personal_email']) > 100:
            errors.append("Email must be less than 100 characters")

    # Employment Details
    if not data.get('role') or len(data.get('role', '').strip()) == 0:
        errors.append("Role is required")

    if not data.get('joining_date'):
        errors.append("Joining date is required")
    else:
        try:
            datetime.strptime(data['joining_date'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid joining date format. Use YYYY-MM-DD")

    return errors


# ============================================
# GET CURRENT USER'S STAFF RECORD
# ============================================
@staff_bp.route('/me', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_current_user_staff():
    """Get staff record for current logged-in user"""
    try:
        current_user_id = get_jwt_identity()
        staff = Staff.query.filter_by(user_id=current_user_id).first()

        if not staff:
            return not_found_response("Staff", details="Staff record not found for this user")

        return success_response(staff.to_dict(), "Staff record retrieved successfully")

    except Exception as e:
        logger.error(f"Get current user staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve staff record")


# ============================================
# GET ALL STAFF (With Pagination & Filtering)
# ============================================
@staff_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def get_staff():
    """Get all staff with pagination and filtering"""
    try:
        # Get current user's company_id for multi-tenant filtering
        current_user_id = get_jwt_identity()
        if current_user_id:
            current_user = User.query.get(int(current_user_id))
            if not current_user:
                return error_response("Current user not found", status_code=401)
            company_id = current_user.company_id
        else:
            # If no JWT, try to get company_id from query params or return error
            return error_response("Authentication required", status_code=401)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role', None, type=str)
        search = request.args.get('search', None, type=str)

        if page <= 0 or per_page <= 0:
            return error_response("Page and per_page must be positive integers", status_code=400)

        query = Staff.query.filter_by(company_id=company_id)

        # Apply filters
        if role:
            query = query.filter(Staff.role.ilike(f"%{role}%"))

        if search:
            query = query.filter(
                db.or_(
                    Staff.first_name.ilike(f"%{search}%"),
                    Staff.last_name.ilike(f"%{search}%"),
                    Staff.personal_phone.ilike(f"%{search}%"),
                    Staff.personal_email.ilike(f"%{search}%")
                )
            )

        # Apply pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginated_response(
            items=[s.to_dict() for s in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Staff retrieved successfully"
        )
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        logger.error(f"Get staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve staff")


# ============================================
# GET STAFF BY ID
# ============================================
@staff_bp.route('/<int:staff_id>', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def get_staff_by_id(staff_id):
    """Get staff by ID"""
    try:
        staff = Staff.query.get(staff_id)

        if not staff:
            return not_found_response("Staff", details=f"No staff with ID {staff_id} found")

        return success_response(staff.to_dict(), "Staff retrieved successfully")
    except Exception as e:
        logger.error(f"Get staff by ID error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve staff record")


# ============================================
# CREATE STAFF
# ============================================
@staff_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_staff():
    """Create new staff member with optional user account"""
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        data = request.get_json(silent=True) or {}

        # Validate data
        errors = []
        for err in validate_staff_data(data):
            errors.append({"field": "staff", "message": err})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Get current user's company_id (required for multi-tenant support)
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return error_response("Current user not found", status_code=401)

        # Check for duplicate phone within the same company
        phone = data.get('personal_phone', data.get('phone', ''))
        existing = Staff.query.filter_by(personal_phone=phone, company_id=current_user.company_id).first()
        if existing:
            return error_response("Staff member with this phone already exists in your company", status_code=409)

        # Generate User ID automatically
        user_id = UserIDGenerator.generate_user_id(current_user.company_id)

        # Create new staff with formal fields
        full_name = data.get('name', '').strip()
        first_name = data.get('first_name', full_name.split()[0] if full_name else '').strip()
        last_name = data.get('last_name', ' '.join(full_name.split()[1:]) if full_name else '').strip()

        # Parse joining_date (handle multiple formats)
        joining_date = None
        if data.get('joining_date'):
            try:
                # Try YYYY-MM-DD format first
                joining_date = datetime.strptime(data['joining_date'], '%Y-%m-%d').date()
            except ValueError:
                try:
                    # Try DD/MM/YYYY format
                    joining_date = datetime.strptime(data['joining_date'], '%d/%m/%Y').date()
                except ValueError:
                    joining_date = datetime.now().date()
        else:
            joining_date = datetime.now().date()

        # Parse date_of_birth if provided
        date_of_birth = None
        if data.get('date_of_birth'):
            try:
                date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                try:
                    date_of_birth = datetime.strptime(data['date_of_birth'], '%d/%m/%Y').date()
                except ValueError:
                    date_of_birth = None

        # Parse license_expiry if provided
        license_expiry = None
        if data.get('license_expiry'):
            try:
                license_expiry = datetime.strptime(data['license_expiry'], '%Y-%m-%d').date()
            except ValueError:
                try:
                    license_expiry = datetime.strptime(data['license_expiry'], '%d/%m/%Y').date()
                except ValueError:
                    license_expiry = None

        staff = Staff(
            company_id=current_user.company_id or 1,  # Default to company_id 1 if not set
            staff_id=user_id,  # Store generated User ID
            name=full_name or f"{first_name} {last_name}".strip(),  # Legacy name field
            # Personal Information
            first_name=first_name,
            last_name=last_name,
            father_name=data.get('father_name', '').strip() if data.get('father_name') else None,
            date_of_birth=date_of_birth,
            gender=data.get('gender'),
            # Contact Information
            # Legacy fields
            email=data.get('email', '').strip() if data.get('email') else None,
            phone=data.get('phone', '').strip() if data.get('phone') else data.get('personal_phone', '').strip(),
            # New fields
            personal_email=data.get('personal_email', data.get('email', '')).strip() if data.get('personal_email') or data.get('email') else None,
            personal_phone=data.get('personal_phone', data.get('phone', '')).strip(),
            alternate_phone=data.get('alternate_phone', '').strip() if data.get('alternate_phone') else None,
            # Present Address
            present_address=data.get('present_address'),
            present_city=data.get('present_city'),
            present_state=data.get('present_state'),
            present_pincode=data.get('present_pincode'),
            # Permanent Address
            permanent_address=data.get('permanent_address'),
            permanent_city=data.get('permanent_city'),
            permanent_state=data.get('permanent_state'),
            permanent_pincode=data.get('permanent_pincode'),
            # Employment Details
            designation=data.get('designation'),
            department=data.get('department'),
            role=data.get('role', 'worker').strip(),
            joining_date=joining_date,
            employment_type=data.get('employment_type'),
            # Qualifications
            highest_qualification=data.get('highest_qualification'),
            specialization=data.get('specialization'),
            license_number=data.get('license_number'),
            license_expiry=license_expiry,
            # Bank Details
            bank_name=data.get('bank_name'),
            account_number=data.get('account_number'),
            ifsc_code=data.get('ifsc_code'),
            account_holder_name=data.get('account_holder_name'),
            # Emergency Contact
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            emergency_contact_relation=data.get('emergency_contact_relation'),
            # Financial Details
            # Legacy fields
            salary=float(data.get('salary', 0)),
            pf=float(data.get('pf', 0)),
            esi=float(data.get('esi', 0)),
            # New fields
            monthly_salary=float(data.get('monthly_salary', data.get('salary', 0))),
            ctc=float(data.get('ctc', 0)),
            pf_applicable=data.get('pf_applicable', True),
            pf_percentage=float(data.get('pf_percentage', data.get('pf', 12.0))),
            pf_account_number=data.get('pf_account_number'),
            esi_applicable=data.get('esi_applicable', True),
            esi_percentage=float(data.get('esi_percentage', data.get('esi', 0.75))),
            esi_account_number=data.get('esi_account_number'),
            professional_tax_applicable=data.get('professional_tax_applicable', True),
            professional_tax_state=data.get('professional_tax_state'),
            professional_tax_amount=float(data.get('professional_tax_amount', 0)),
            pan_number=data.get('pan_number'),
            income_tax_regime=data.get('income_tax_regime', 'Old'),
            lic_premium=float(data.get('lic_premium', 0)),
            loan_deduction=float(data.get('loan_deduction', 0)),
            other_deductions=float(data.get('other_deductions', 0)),
            # Status
            status='Active',
            photo=data.get('photo'),
            needs_user_access=True,
            user_created_at=datetime.utcnow()
        )

        db.session.add(staff)
        db.session.flush()  # Get the staff ID without committing

        # Always create user account for new staff
        user_info = None
        user, generated_user_id, default_password = UserCreationService.create_user_for_staff(
            {
                'first_name': staff.first_name,
                'last_name': staff.last_name,
                'personal_email': staff.personal_email,
                'role': staff.role
            },
            current_user.company_id
        )

        if user:
            db.session.add(user)
            db.session.flush()  # Get the user ID

            # Link staff to user
            staff.user_id = user.id
            staff.needs_user_access = True

            user_info = {
                "user_id": generated_user_id,
                "username": generated_user_id,
                "default_password": default_password,
                "password_change_required": True,
                "message": "User account created. Default password: Erp@123 — must change on first login."
            }

            # Send welcome email with credentials
            if staff.personal_email:
                from utils.email_utils import send_welcome_email
                from company_settings.models import Company
                employee_full_name = f"{staff.first_name} {staff.last_name}".strip()
                company = Company.query.get(current_user.company_id)
                company_name = company.name if company else "Construction Management System"

                email_sent = send_welcome_email(
                    employee_email=staff.personal_email,
                    employee_name=employee_full_name,
                    username=generated_user_id,
                    password=default_password,
                    company_name=company_name
                )

                user_info["email_sent"] = email_sent
                if email_sent:
                    print(f"✅ Welcome email sent to {staff.personal_email}")
                else:
                    print(f"⚠️ Failed to send welcome email to {staff.personal_email}")
        else:
            # Log error if user creation fails
            print(f"Warning: Failed to create user account for staff {staff.staff_id}")

        db.session.commit()

        # ✅ LOG ACTIVITY
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=current_user.company_id,
            entity_type='Staff',
            entity_id=staff.id,
            action='CREATE',
            new_values=staff.to_dict(),
            entity_name=f"{staff.first_name} {staff.last_name}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Notify admin about new staff creation
        try:
            from notifications.models import Notification
            notif = Notification(
                user_id=int(current_user_id),
                company_id=current_user.company_id,
                title='New Staff Added',
                message=f'{staff.first_name} {staff.last_name} ({staff.role}) has been added to the team.',
                notification_type='staff',
                related_model='staff',
                related_id=staff.id
            )
            db.session.add(notif)
            db.session.commit()
            print(f"[NOTIFICATION] Staff creation notification sent to user #{current_user_id}")
        except Exception as e:
            print(f"[NOTIFICATION ERROR] Could not send staff creation notification: {str(e)}")
            db.session.rollback()

        response_data = staff.to_dict()
        if user_info:
            response_data['user_info'] = user_info

        return success_response(response_data, "Staff member created successfully", status_code=201)
    except IntegrityError as e:
        db.session.rollback()
        if 'UNIQUE constraint' in str(e):
            if 'phone' in str(e).lower():
                return error_response(
                    "Phone number already registered",
                    details="This phone number is already in use within your company",
                    status_code=409
                )
            elif 'email' in str(e).lower():
                return error_response(
                    "Email already registered",
                    details="This email is already in use",
                    status_code=409
                )
        return error_response("Database constraint violated", status_code=400)
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except TypeError as e:
        db.session.rollback()
        return error_response(f"Type error in request: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Staff creation error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create staff record")


# ============================================
# UPDATE STAFF
# ============================================
@staff_bp.route('/<int:staff_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_staff(staff_id):
    """Update staff member"""
    try:
        from admin_management.utils.activity_logger import log_entity_action

        staff = Staff.query.get(staff_id)

        if not staff:
            return not_found_response("Staff", details=f"No staff with ID {staff_id} found")

        data = request.get_json(silent=True) or {}

        # Capture old values BEFORE update
        old_values = staff.to_dict()

        # Validate data (only for fields being updated)
        if any(k in data for k in ['name', 'role', 'phone', 'email', 'joining_date', 'salary', 'pf', 'esi']):
            # Create temp dict with all fields for validation
            full_name = f"{staff.first_name} {staff.last_name}".strip()
            temp_data = {
                'name': data.get('name', full_name),
                'role': data.get('role', staff.role),
                'phone': data.get('phone', staff.personal_phone or ''),
                'email': data.get('email', staff.personal_email or ''),
                'joining_date': data.get('joining_date', staff.joining_date.strftime('%Y-%m-%d') if staff.joining_date else ''),
                'salary': data.get('salary', staff.monthly_salary),
                'pf': data.get('pf', staff.pf_percentage),
                'esi': data.get('esi', staff.esi_percentage)
            }
            errors = []
            for err in validate_staff_data(temp_data):
                errors.append({"field": "staff", "message": err})
            if errors:
                return error_response("Validation failed", errors=errors, status_code=400)

        # Update fields
        if 'name' in data:
            name_parts = data['name'].strip().split()
            staff.name = data['name'].strip()  # Update legacy name field
            staff.first_name = name_parts[0] if name_parts else ''
            staff.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        if 'role' in data:
            staff.role = data['role'].strip()
        if 'phone' in data:
            # Check for duplicate phone (excluding current staff)
            existing = Staff.query.filter(
                Staff.personal_phone == data['phone'],
                Staff.id != staff_id
            ).first()
            if existing:
                return error_response("Another staff member with this phone already exists", status_code=409)
            staff.phone = data['phone'].strip()  # Legacy field
            staff.personal_phone = data['phone'].strip()
        if 'email' in data:
            staff.email = data['email'].strip() if data.get('email') else None  # Legacy field
            staff.personal_email = data['email'].strip() if data.get('email') else None
        if 'joining_date' in data:
            staff.joining_date = datetime.strptime(data['joining_date'], '%Y-%m-%d').date()
        if 'salary' in data:
            staff.monthly_salary = float(data['salary'])
        if 'pf' in data:
            staff.pf_percentage = float(data['pf'])
        if 'esi' in data:
            staff.esi_percentage = float(data['esi'])
        if 'photo' in data:
            staff.photo = data['photo']

        # Update user account if staff has one and name/email changed
        if staff.user_id:
            user = User.query.get(staff.user_id)
            if user:
                if 'name' in data:
                    user.name = data['name'].strip()
                if 'email' in data:
                    user.email = data['email'].strip() if data.get('email') else None

        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Staff',
            entity_id=staff.id,
            action='UPDATE',
            old_values=old_values,
            new_values=staff.to_dict(),
            entity_name=f"{staff.first_name} {staff.last_name}".strip(),
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(staff.to_dict(), "Staff member updated successfully")
    except IntegrityError as e:
        db.session.rollback()
        if 'UNIQUE constraint' in str(e):
            if 'phone' in str(e).lower():
                return error_response(
                    "Phone number already in use",
                    details="This phone number is already registered",
                    status_code=409
                )
        return error_response("Database constraint violation", status_code=400)
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Staff update error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update staff record")


# ============================================
# DELETE STAFF
# ============================================
@staff_bp.route('/<int:staff_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_staff(staff_id):
    """Delete staff member"""
    try:
        from admin_management.utils.activity_logger import log_entity_action

        staff = Staff.query.get(staff_id)

        if not staff:
            return not_found_response("Staff", details=f"No staff with ID {staff_id} found")

        # Capture data BEFORE delete
        deleted_data = staff.to_dict()
        staff_name = f"{staff.first_name} {staff.last_name}".strip()

        db.session.delete(staff)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Staff',
            entity_id=staff_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=staff_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Staff member deleted successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Staff deletion error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete staff record")


# ============================================
# BULK DELETE STAFF
# ============================================
@staff_bp.route('/bulk/delete', methods=['POST'], strict_slashes=False)
@jwt_required()
def bulk_delete_staff():
    """Delete multiple staff members"""
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        data = request.get_json(silent=True) or {}
        ids = data.get('ids', [])

        if not ids or not isinstance(ids, list):
            return error_response("Invalid IDs provided", status_code=400)

        Staff.query.filter(Staff.id.in_(ids)).delete()
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Staff',
            entity_id=None,
            action='BULK_DELETE',
            old_values={'ids': ids},
            entity_name=f"Bulk delete of {len(ids)} staff members",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message=f"{len(ids)} staff members deleted successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk delete error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete staff members")


# ============================================
# EXPENSE MANAGEMENT ENDPOINTS
# ============================================

@staff_bp.route('/expenses', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_expenses():
    """Get expenses with filtering, sorting, and pagination"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return error_response("Current user not found", status_code=401)

        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        date_start = request.args.get('date_start', None, type=str)
        date_end = request.args.get('date_end', None, type=str)
        staff_id = request.args.get('staff_id', None, type=int)
        project_id = request.args.get('project_id', None, type=int)
        status = request.args.get('status', None, type=str)
        category = request.args.get('category', None, type=str)

        if page <= 0 or per_page <= 0:
            return error_response("Page and per_page must be positive integers", status_code=400)

        # Base query filtered by company
        query = Expense.query.filter_by(company_id=current_user.company_id)

        # Apply filters
        if date_start:
            try:
                start_date = datetime.strptime(date_start, '%Y-%m-%d').date()
                query = query.filter(Expense.expense_date >= start_date)
            except ValueError:
                return error_response("Invalid date_start format. Use YYYY-MM-DD", status_code=400)

        if date_end:
            try:
                end_date = datetime.strptime(date_end, '%Y-%m-%d').date()
                query = query.filter(Expense.expense_date <= end_date)
            except ValueError:
                return error_response("Invalid date_end format. Use YYYY-MM-DD", status_code=400)

        if staff_id:
            query = query.filter_by(staff_id=staff_id)

        if project_id:
            query = query.filter_by(project_id=project_id)

        if status:
            query = query.filter_by(status=status)

        if category:
            query = query.filter_by(category=category)

        # Pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginated_response(
            items=[e.to_dict() for e in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Expenses retrieved successfully"
        )

    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        logger.error(f"Get expenses error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve expenses")


@staff_bp.route('/approvals/expenses', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_expense_approvals():
    """Get pending expenses for approval with 2-tier filtering (finance/manager only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return error_response("Current user not found", status_code=401)

        # Check if user has permission to approve (finance, manager, or admin)
        if current_user.role not in ['finance', 'manager', 'admin']:
            return error_response("You do not have permission to view expense approvals", status_code=403)

        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', 'pending', type=str)
        category = request.args.get('category', None, type=str)
        approval_tier = request.args.get('approval_tier', None, type=str)  # New: filter by tier

        if page <= 0 or per_page <= 0:
            return error_response("Page and per_page must be positive integers", status_code=400)

        # Base query: all expenses from the company, not filtered by staff_id
        query = Expense.query.filter_by(company_id=current_user.company_id)

        # Default to pending status if not specified
        if status:
            # Case-insensitive comparison
            query = query.filter(Expense.status.ilike(status))
        else:
            query = query.filter(Expense.status.ilike('pending'))

        # Apply category filter if provided
        if category:
            query = query.filter(Expense.category.ilike(category))

        # NEW: Filter by approval tier and stage if provided
        # approval_tier can be: 'Tier1', 'Tier2_first', 'Tier2_second'
        if approval_tier:
            if approval_tier == 'Tier1':
                # Tier1: Show all pending Tier1 expenses
                query = query.filter(Expense.approval_tier == 'Tier1')
            elif approval_tier == 'Tier2_first':
                # Tier2 First Approval: Show Tier2 expenses with 0 approvals
                query = query.filter(Expense.approval_tier == 'Tier2')
                query = query.filter(Expense.approvals_received == 0)
            elif approval_tier == 'Tier2_second':
                # Tier2 Second Approval: Show Tier2 expenses with 1 approval
                query = query.filter(Expense.approval_tier == 'Tier2')
                query = query.filter(Expense.approvals_received == 1)
            else:
                return error_response("approval_tier must be 'Tier1', 'Tier2_first', or 'Tier2_second'", status_code=400)

        # Sort by date descending (newest first)
        query = query.order_by(Expense.expense_date.desc())

        # Pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginated_response(
            items=[e.to_dict() for e in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Pending expenses for approval retrieved successfully"
        )

    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        logger.error(f"Get expense approvals error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve pending expenses")


@staff_bp.route('/expenses/<int:expense_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_expense(expense_id):
    """Get expense by ID"""
    try:
        expense = Expense.query.get(expense_id)
        if not expense:
            return not_found_response("Expense", details=f"No expense with ID {expense_id} found")

        return success_response(expense.to_dict(), "Expense retrieved successfully")

    except Exception as e:
        logger.error(f"Get expense error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve expense")


@staff_bp.route('/expenses', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_expense():
    """Create new expense"""
    try:
        from admin_management.utils.activity_logger import log_entity_action

        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return error_response("Current user not found", status_code=401)

        data = request.get_json(silent=True) or {}

        # Validate required fields
        errors = []
        if not data.get('staff_id'):
            errors.append("Staff ID is required")
        if not data.get('project_id'):
            errors.append("Project ID is required")
        if not data.get('expense_date'):
            errors.append("Expense date is required")
        if not data.get('category'):
            errors.append("Category is required")
        if not data.get('description'):
            errors.append("Description is required")
        if 'amount' not in data or data.get('amount') is None:
            errors.append("Amount is required")
        else:
            try:
                float(data['amount'])
                if float(data['amount']) <= 0:
                    errors.append("Amount must be greater than 0")
            except (ValueError, TypeError):
                errors.append("Amount must be a valid number")

        if errors:
            return error_response("Validation failed", errors=[{"field": "expense", "message": e} for e in errors], status_code=400)

        # Check if staff and project exist
        staff = Staff.query.get(data['staff_id'])
        if not staff:
            return error_response("Staff not found", status_code=404)

        from project_management.models.models import Project
        project = Project.query.get(data['project_id'])
        if not project:
            return error_response("Project not found", status_code=404)

        # Check if staff is assigned to this project (permission check)
        from project_management.models.models import ProjectAssignment
        has_permission = ProjectAssignment.query.filter_by(
            staff_id=data['staff_id'],
            project_id=data['project_id']
        ).first()

        if not has_permission:
            return error_response(
                "This staff member is not assigned to this project",
                status_code=403
            )

        # Create expense (always start as Pending - must be approved via approval endpoint)
        amount = float(data['amount'])

        # Determine approval tier based on amount
        # Tier 1: ≤₹50,000 (1 approver)
        # Tier 2: >₹50,000 (2 approvers)
        approval_tier = 'Tier2' if amount > 50000 else 'Tier1'
        approvals_required = 2 if amount > 50000 else 1

        expense = Expense(
            company_id=current_user.company_id,
            staff_id=data['staff_id'],
            project_id=data['project_id'],
            expense_date=datetime.strptime(data['expense_date'], '%Y-%m-%d').date(),
            category=data['category'],
            description=data['description'],
            amount=amount,
            receipt_url=data.get('receipt_url'),
            status='Pending',  # ALWAYS pending - no bypassing approval workflow
            approval_tier=approval_tier,
            approvals_required=approvals_required,
            approvals_received=0
        )

        db.session.add(expense)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=current_user.company_id,
            entity_type='Expense',
            entity_id=expense.id,
            action='CREATE',
            new_values=expense.to_dict(),
            entity_name=f"Expense - {expense.category}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(expense.to_dict(), "Expense created successfully", status_code=201)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create expense error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create expense")


@staff_bp.route('/expenses/<int:expense_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_expense(expense_id):
    """Update expense - ONLY non-approval fields can be edited"""
    try:
        from admin_management.utils.activity_logger import log_entity_action

        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return error_response("Current user not found", status_code=401)

        expense = Expense.query.get(expense_id)
        if not expense:
            return not_found_response("Expense", details=f"No expense with ID {expense_id} found")

        data = request.get_json(silent=True) or {}
        old_values = expense.to_dict()

        # SECURITY: Prevent status changes via update endpoint
        # Status can ONLY be changed via dedicated approve/reject endpoints
        if 'status' in data and data['status'] != expense.status:
            return error_response(
                "Status changes are not allowed via update. Use /approve or /reject endpoints instead.",
                status_code=403
            )

        # Update allowed fields only
        if 'amount' in data:
            try:
                float(data['amount'])
                if float(data['amount']) <= 0:
                    return error_response("Amount must be greater than 0", status_code=400)
                expense.amount = float(data['amount'])
            except (ValueError, TypeError):
                return error_response("Amount must be a valid number", status_code=400)

        if 'category' in data:
            expense.category = data['category']

        if 'description' in data:
            expense.description = data['description']

        if 'receipt_url' in data:
            expense.receipt_url = data['receipt_url']

        # Rejection reason can only be set when rejecting (via reject endpoint)
        if 'rejection_reason' in data:
            return error_response(
                "Rejection reasons cannot be set via update. Use /reject endpoint instead.",
                status_code=403
            )

        db.session.commit()

        # Log activity
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Expense',
            entity_id=expense.id,
            action='UPDATE',
            old_values=old_values,
            new_values=expense.to_dict(),
            entity_name=f"Expense - {expense.category}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(expense.to_dict(), "Expense updated successfully")

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update expense error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update expense")


@staff_bp.route('/expenses/<int:expense_id>/approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def approve_expense(expense_id):
    """Approve a pending expense - Tier 1 (≤₹50K) or first approval for Tier 2 (>₹50K)"""
    try:
        from admin_management.utils.activity_logger import log_entity_action

        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        # Check if user exists
        if not user:
            return error_response("User not found", status_code=401)

        # SECURITY: Only Finance, Manager, or Admin can approve expenses
        if user.role not in ['finance', 'manager', 'admin']:
            return error_response(
                "You do not have permission to approve expenses. Only Finance, Manager, or Admin can approve.",
                status_code=403
            )

        expense = Expense.query.get(expense_id)
        if not expense:
            return not_found_response("Expense", details=f"No expense with ID {expense_id} found")

        if expense.status != 'Pending':
            return error_response(f"Cannot approve expense with status '{expense.status}'. Only pending expenses can be approved.", status_code=400)

        old_values = expense.to_dict()

        # Handle 2-tier approval system
        if expense.approval_tier == 'Tier1':
            # Tier 1: Single approval completes the process
            expense.status = 'Approved'
            expense.approved_by = int(current_user_id)
            expense.approved_date = datetime.utcnow()
            expense.first_approver_id = int(current_user_id)
            expense.first_approval_date = datetime.utcnow()
            expense.approvals_received = 1
            approval_message = "Expense approved successfully (Tier 1 - Single Approval)"

        elif expense.approval_tier == 'Tier2':
            # Tier 2: Track multiple approvals
            if expense.approvals_received == 0:
                # First approval
                expense.first_approver_id = int(current_user_id)
                expense.first_approval_date = datetime.utcnow()
                expense.approvals_received = 1
                approval_message = f"First approval recorded. Awaiting second approval (1/2)"
            elif expense.approvals_received == 1:
                # Second approval - check that it's a different person
                if expense.first_approver_id == int(current_user_id):
                    return error_response("The same person cannot approve twice. A different approver is required.", status_code=400)

                expense.status = 'Approved'
                expense.second_approver_id = int(current_user_id)
                expense.second_approval_date = datetime.utcnow()
                expense.approvals_received = 2
                expense.approved_by = int(current_user_id)  # Use the second approver as the final approval
                expense.approved_date = datetime.utcnow()
                approval_message = "Expense approved successfully (Tier 2 - Both Approvals Complete)"
            else:
                return error_response("This expense has already been fully approved.", status_code=400)
        else:
            return error_response("Unknown approval tier", status_code=400)

        # Commit the expense approval first (this is the critical operation)
        db.session.commit()
        print(f"Expense {expense.id} approval processed successfully. Tier: {expense.approval_tier}, Approvals: {expense.approvals_received}/{expense.approvals_required}")

        # Create transaction in Finance module ONLY when fully approved
        if expense.status == 'Approved':
            try:
                from finance_management.models.cash_transaction import CashTransaction
                from project_management.models.models import Project

                # Get staff and project names
                staff = Staff.query.get(expense.staff_id) if expense.staff_id else None
                project = Project.query.get(expense.project_id) if expense.project_id else None
                staff_name = f"{staff.first_name} {staff.last_name}".strip() if staff else "Unknown"
                project_name = project.name if project else "Unknown"

                cash_tx = CashTransaction(
                    amount=expense.amount,
                    type='expense',
                    category=expense.category,
                    date=expense.expense_date,
                    description=f"{expense.category} - {expense.description}",
                    project_id=expense.project_id,
                    project_name=project_name,
                    staff_id=expense.staff_id,
                    staff_name=staff_name,
                    created_by=int(current_user_id)
                )
                db.session.add(cash_tx)
                db.session.commit()
                print(f"CashTransaction created for fully approved expense {expense.id} - {staff_name} / {project_name}")
            except Exception as tx_error:
                print(f"Warning: Could not create cash transaction for expense: {str(tx_error)}")
                db.session.rollback()
                # Expense approval already succeeded - this is just a warning

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Expense',
            entity_id=expense.id,
            action='APPROVE',
            old_values=old_values,
            new_values=expense.to_dict(),
            entity_name=f"Expense - {expense.category} (₹{expense.amount})",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Notify staff member about expense approval
        try:
            from notifications.models import Notification
            if expense.staff_id:
                expense_staff = Staff.query.get(expense.staff_id)
                if expense_staff and expense_staff.user_id:
                    notif = Notification(
                        user_id=expense_staff.user_id,
                        company_id=user.company_id,
                        title='Expense Approved',
                        message=f'Your {expense.category} expense of Rs.{expense.amount:.2f} has been approved.',
                        notification_type='expense',
                        related_model='expense',
                        related_id=expense.id
                    )
                    db.session.add(notif)
                    db.session.commit()
                    print(f"[NOTIFICATION] Expense approval notification sent to user #{expense_staff.user_id}")
        except Exception as e:
            print(f"[NOTIFICATION ERROR] Could not send expense approval notification: {str(e)}")
            db.session.rollback()

        return success_response(expense.to_dict(), approval_message)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Approve expense error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to approve expense")


@staff_bp.route('/expenses/<int:expense_id>/reject', methods=['POST'], strict_slashes=False)
@jwt_required()
def reject_expense(expense_id):
    """Reject a pending expense - FINANCE/MANAGER/ADMIN only"""
    try:
        from admin_management.utils.activity_logger import log_entity_action

        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        # Check if user exists
        if not user:
            return error_response("User not found", status_code=401)

        # SECURITY: Only Finance, Manager, or Admin can reject expenses
        if user.role not in ['finance', 'manager', 'admin']:
            return error_response(
                "You do not have permission to reject expenses. Only Finance, Manager, or Admin can reject.",
                status_code=403
            )

        expense = Expense.query.get(expense_id)
        if not expense:
            return not_found_response("Expense", details=f"No expense with ID {expense_id} found")

        if expense.status != 'Pending':
            return error_response(f"Cannot reject expense with status '{expense.status}'. Only pending expenses can be rejected.", status_code=400)

        data = request.get_json(silent=True) or {}
        rejection_reason = data.get('rejection_reason', 'No reason provided')

        old_values = expense.to_dict()

        # Update status and rejection info
        expense.status = 'Rejected'
        expense.rejection_reason = rejection_reason

        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Expense',
            entity_id=expense.id,
            action='REJECT',
            old_values=old_values,
            new_values=expense.to_dict(),
            entity_name=f"Expense - {expense.category} (₹{expense.amount})",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Notify staff member about expense rejection
        try:
            from notifications.models import Notification
            if expense.staff_id:
                expense_staff = Staff.query.get(expense.staff_id)
                if expense_staff and expense_staff.user_id:
                    notif = Notification(
                        user_id=expense_staff.user_id,
                        company_id=user.company_id,
                        title='Expense Rejected',
                        message=f'Your {expense.category} expense of Rs.{expense.amount:.2f} was rejected. Reason: {rejection_reason}',
                        notification_type='expense',
                        related_model='expense',
                        related_id=expense.id
                    )
                    db.session.add(notif)
                    db.session.commit()
                    print(f"[NOTIFICATION] Expense rejection notification sent to user #{expense_staff.user_id}")
        except Exception as e:
            print(f"[NOTIFICATION ERROR] Could not send expense rejection notification: {str(e)}")
            db.session.rollback()

        return success_response(expense.to_dict(), f"Expense rejected successfully. Reason: {rejection_reason}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Reject expense error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to reject expense")


@staff_bp.route('/expenses/<int:expense_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_expense(expense_id):
    """Delete expense"""
    try:
        from admin_management.utils.activity_logger import log_entity_action

        expense = Expense.query.get(expense_id)
        if not expense:
            return not_found_response("Expense", details=f"No expense with ID {expense_id} found")

        deleted_data = expense.to_dict()

        db.session.delete(expense)
        db.session.commit()

        # Log activity
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Expense',
            entity_id=expense_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=f"Expense - {deleted_data['category']}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Expense deleted successfully")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete expense error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete expense")


@staff_bp.route('/expenses/batch/approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def batch_approve_expenses():
    """Approve multiple expenses and create finance transactions"""
    try:
        from admin_management.utils.activity_logger import log_entity_action
        from finance_management.models.cash_transaction import CashTransaction
        from project_management.models.models import Project

        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user:
            return error_response("Current user not found", status_code=401)

        data = request.get_json(silent=True) or {}
        expense_ids = data.get('expense_ids', [])

        if not expense_ids or not isinstance(expense_ids, list):
            return error_response("Invalid expense_ids provided", status_code=400)

        # Fetch expenses before updating (to get details for CashTransaction)
        expenses = Expense.query.filter(Expense.id.in_(expense_ids)).all()

        # Update all expenses to Approved
        Expense.query.filter(Expense.id.in_(expense_ids)).update(
            {
                'status': 'Approved',
                'approved_by': int(current_user_id),
                'approved_date': datetime.utcnow()
            },
            synchronize_session=False
        )
        db.session.commit()

        # Create CashTransaction for each approved expense
        tx_count = 0
        for expense in expenses:
            try:
                staff = Staff.query.get(expense.staff_id) if expense.staff_id else None
                project = Project.query.get(expense.project_id) if expense.project_id else None
                staff_name = f"{staff.first_name} {staff.last_name}".strip() if staff else "Unknown"
                project_name = project.name if project else "Unknown"

                cash_tx = CashTransaction(
                    amount=expense.amount,
                    type='expense',
                    category=expense.category,
                    date=expense.expense_date,
                    description=f"{expense.category} - {expense.description}",
                    project_id=expense.project_id,
                    project_name=project_name,
                    staff_id=expense.staff_id,
                    staff_name=staff_name,
                    created_by=int(current_user_id)
                )
                db.session.add(cash_tx)
                tx_count += 1
            except Exception as tx_error:
                print(f"Warning: Could not create cash transaction for expense {expense.id}: {str(tx_error)}")

        db.session.commit()
        print(f"Created {tx_count} CashTransaction records for batch-approved expenses")

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id,
            entity_type='Expense',
            entity_id=None,
            action='BULK_APPROVE',
            new_values={'expense_ids': expense_ids, 'status': 'Approved'},
            entity_name=f"Bulk approve {len(expense_ids)} expenses",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message=f"{len(expense_ids)} expenses approved successfully")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Batch approve expenses error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to approve expenses")


# ============================================
# MOBILE APP - ASSIGNED PROJECTS & VEHICLES
# ============================================

@staff_bp.route('/<int:staff_id>/projects', methods=['GET'])
@jwt_required()
def get_assigned_projects(staff_id):
    """
    Get all projects assigned to a staff member (for mobile app role-based access)

    Returns:
        List of projects with basic details
    """
    try:
        # Get the staff member
        staff = Staff.query.get(staff_id)
        if not staff:
            return not_found_response("Staff member not found")

        # Get assigned projects through ProjectAssignment relationship
        from project_management.models.project_assignment import ProjectAssignment
        from project_management.models.models import Project

        assignments = ProjectAssignment.query.filter(
            ProjectAssignment.staff_id == staff_id,
            ProjectAssignment.removed_on == None  # Only active assignments
        ).all()

        projects = []
        for assignment in assignments:
            project = Project.query.get(assignment.project_id)
            if project:
                projects.append({
                    'id': project.id,
                    'name': project.name,
                    'status': project.status,
                    'location': project.location,
                    'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                })

        return success_response(data=projects, message=f"Found {len(projects)} assigned projects")

    except Exception as e:
        logger.error(f"Get assigned projects error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve assigned projects")


@staff_bp.route('/expenses/mobile', methods=['POST'])
@jwt_required()
def create_expense_mobile():
    """
    Create new expense from mobile app (simplified endpoint)
    """
    try:
        from admin_management.utils.activity_logger import log_entity_action

        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user:
            return error_response("Current user not found", status_code=401)

        data = request.get_json(silent=True) or {}

        # Log incoming data for debugging
        print(f"Mobile Expense Data: {data}")

        # Validate required fields
        errors = []
        if not data.get('staff_id'):
            errors.append("Staff ID is required")
        if not data.get('project_id'):
            errors.append("Project ID is required")
        if not data.get('expense_date'):
            errors.append("Expense date is required")
        if not data.get('category'):
            errors.append("Category is required")
        if not data.get('description'):
            errors.append("Description is required")
        if 'amount' not in data or data.get('amount') is None:
            errors.append("Amount is required")

        if errors:
            return error_response("Validation failed", errors=[{"field": "expense", "message": e} for e in errors], status_code=400)

        try:
            amount = float(data['amount'])
            if amount <= 0:
                return error_response("Amount must be greater than 0", status_code=400)
        except (ValueError, TypeError):
            return error_response("Amount must be a valid number", status_code=400)

        # Check if staff exists
        staff = Staff.query.get(data['staff_id'])
        if not staff:
            return error_response("Staff member not found", status_code=404)

        # Create expense with minimal validation (always start as Pending)
        expense = Expense(
            company_id=current_user.company_id,
            staff_id=data['staff_id'],
            project_id=data['project_id'],
            expense_date=datetime.strptime(data['expense_date'], '%Y-%m-%d').date(),
            category=data['category'],
            description=data['description'],
            amount=float(data['amount']),
            receipt_url=data.get('receipt_url'),
            status='Pending'  # ALWAYS pending - no bypassing approval workflow
        )

        db.session.add(expense)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=current_user.company_id,
            entity_type='Expense',
            entity_id=expense.id,
            action='CREATE',
            new_values=expense.to_dict(),
            entity_name=f"Expense - {expense.category}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Notify admin/manager/finance about new expense
        try:
            from notifications.models import Notification
            from user_management.models import User as UserModel
            admin_users = UserModel.query.filter(
                UserModel.company_id == current_user.company_id,
                UserModel.role.in_(['admin', 'manager', 'finance']),
                UserModel.is_active == True
            ).all()
            for admin in admin_users:
                notif = Notification(
                    user_id=admin.id,
                    company_id=current_user.company_id,
                    title='New Expense Submitted',
                    message=f'{current_user.username} submitted a {expense.category} expense of Rs.{expense.amount:.2f} for approval.',
                    notification_type='expense',
                    related_model='expense',
                    related_id=expense.id
                )
                db.session.add(notif)
            db.session.commit()
            print(f"[NOTIFICATION] Created {len(admin_users)} notifications for expense #{expense.id}")
        except Exception as e:
            print(f"[NOTIFICATION ERROR] Could not send expense notification: {str(e)}")
            db.session.rollback()

        return success_response(expense.to_dict(), "Expense created successfully", status_code=201)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create expense (mobile) error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create expense")


@staff_bp.route('/<int:staff_id>/vehicles', methods=['GET'])
@jwt_required()
def get_assigned_vehicles(staff_id):
    """
    Get all vehicles assigned to a driver (for mobile app role-based access)

    Returns:
        List of vehicles with document status
    """
    try:
        # Get the staff member (must be a driver)
        staff = Staff.query.get(staff_id)
        if not staff:
            return not_found_response("Staff member not found")

        # Only drivers can have assigned vehicles
        if staff.role and staff.role.lower() != 'driver':
            return success_response(data=[], message="Staff member is not a driver")

        # Get assigned vehicles through DriverVehicleAssignment relationship
        from vehicle_management.driver_assignment import DriverVehicleAssignment
        from vehicle_management.models import Vehicle

        assignments = DriverVehicleAssignment.query.filter(
            DriverVehicleAssignment.driver_id == staff_id,
            DriverVehicleAssignment.unassigned_date == None  # Only active assignments
        ).all()

        vehicles = []
        for assignment in assignments:
            vehicle = Vehicle.query.get(assignment.vehicle_id)
            if vehicle:
                # Format vehicle data for mobile
                vehicle_data = {
                    'id': vehicle.id,
                    'name': f"{vehicle.make} {vehicle.model}",
                    'plate': vehicle.registration_number,
                    'model': vehicle.model,
                    'make': vehicle.make,
                    'year': vehicle.year,
                    'status': vehicle.status or 'Active',
                    'mileage': f"{vehicle.mileage} km" if vehicle.mileage else "N/A",
                    'fuel': 'N/A',  # Can be updated if fuel logs are linked
                    'type': vehicle.type,
                    'documents': [
                        {
                            'name': 'Registration',
                            'expiry': vehicle.registration_date.strftime('%Y-%m-%d') if vehicle.registration_date else 'N/A',
                            'status': 'Valid' if vehicle.registration_date and vehicle.registration_date >= datetime.utcnow().date() else 'Expired'
                        },
                        {
                            'name': 'Insurance',
                            'expiry': vehicle.insurance_date.strftime('%Y-%m-%d') if vehicle.insurance_date else 'N/A',
                            'status': 'Valid' if vehicle.insurance_date and vehicle.insurance_date >= datetime.utcnow().date() else 'Expired'
                        },
                        {
                            'name': 'Pollution Check',
                            'expiry': vehicle.pollution_date.strftime('%Y-%m-%d') if vehicle.pollution_date else 'N/A',
                            'status': 'Valid' if vehicle.pollution_date and vehicle.pollution_date >= datetime.utcnow().date() else 'Expired'
                        },
                        {
                            'name': 'Tax',
                            'expiry': vehicle.tax_date.strftime('%Y-%m-%d') if vehicle.tax_date else 'N/A',
                            'status': 'Valid' if vehicle.tax_date and vehicle.tax_date >= datetime.utcnow().date() else 'Expired'
                        }
                    ]
                }
                vehicles.append(vehicle_data)

        return success_response(data=vehicles, message=f"Found {len(vehicles)} assigned vehicles")

    except Exception as e:
        logger.error(f"Get assigned vehicles error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve assigned vehicles")

