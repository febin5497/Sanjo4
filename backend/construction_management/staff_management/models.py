from extensions import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class Staff(db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # System-generated Staff ID (e.g., STF-2026-001)
    staff_id = db.Column(db.String(50), unique=True, nullable=False)

    # Legacy name field (for backward compatibility with existing database schema)
    name = db.Column(db.String(200), nullable=True)

    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # Male, Female, Other

    # Contact Information
    # Legacy phone field (for backward compatibility)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)  # Legacy email field

    personal_email = db.Column(db.String(100), nullable=True)
    personal_phone = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(20), nullable=True)

    # Present Address
    present_address = db.Column(db.Text, nullable=True)
    present_city = db.Column(db.String(50), nullable=True)
    present_state = db.Column(db.String(50), nullable=True)
    present_pincode = db.Column(db.String(10), nullable=True)

    # Permanent Address
    permanent_address = db.Column(db.Text, nullable=True)
    permanent_city = db.Column(db.String(50), nullable=True)
    permanent_state = db.Column(db.String(50), nullable=True)
    permanent_pincode = db.Column(db.String(10), nullable=True)

    # Employment Details
    designation = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(50), nullable=False)  # Manager, Driver, Site Engineer, Supervisor, Worker
    joining_date = db.Column(db.Date, nullable=False)
    employment_type = db.Column(db.String(50), nullable=True)  # Full-time, Contract, Temporary

    # Qualifications
    highest_qualification = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)  # For drivers
    license_expiry = db.Column(db.Date, nullable=True)  # For drivers

    # Bank Details
    bank_name = db.Column(db.String(100), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    ifsc_code = db.Column(db.String(20), nullable=True)
    account_holder_name = db.Column(db.String(100), nullable=True)

    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    emergency_contact_relation = db.Column(db.String(50), nullable=True)

    # Financial Details - Salary and Deductions
    # Legacy financial fields
    salary = db.Column(db.Float, nullable=False, default=0)
    pf = db.Column(db.Float, nullable=False, default=0)
    esi = db.Column(db.Float, nullable=False, default=0)

    # New financial fields
    monthly_salary = db.Column(db.Float, nullable=True)
    ctc = db.Column(db.Float, nullable=True)  # Cost to Company

    # PF (Provident Fund) - Indian Tax Compliance
    pf_applicable = db.Column(db.Boolean, default=True, nullable=False)
    pf_percentage = db.Column(db.Float, default=12.0, nullable=False)  # Employee contribution %
    pf_account_number = db.Column(db.String(50), nullable=True)  # PRAN or account number

    # ESI (Employee State Insurance) - Indian Tax Compliance
    esi_applicable = db.Column(db.Boolean, default=True, nullable=False)
    esi_percentage = db.Column(db.Float, default=0.75, nullable=False)  # Employee contribution %
    esi_account_number = db.Column(db.String(50), nullable=True)

    # Professional Tax - Indian Tax Compliance
    professional_tax_applicable = db.Column(db.Boolean, default=True, nullable=False)
    professional_tax_state = db.Column(db.String(50), nullable=True)  # State for PT
    professional_tax_amount = db.Column(db.Float, default=0, nullable=False)  # Monthly amount

    # Income Tax
    pan_number = db.Column(db.String(10), nullable=True)  # PAN for income tax
    income_tax_regime = db.Column(db.String(20), default='Old', nullable=False)  # Old or New regime

    # LIC and Other Deductions
    lic_premium = db.Column(db.Float, default=0, nullable=False)
    loan_deduction = db.Column(db.Float, default=0, nullable=False)
    other_deductions = db.Column(db.Float, default=0, nullable=False)

    # Photo
    photo = db.Column(db.String(255), nullable=True)

    # Status & Staff Records
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Left

    # Foreign keys for User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # User access settings
    needs_user_access = db.Column(db.Boolean, default=True)  # Auto-create user account for login
    user_created_at = db.Column(db.DateTime, nullable=True)  # When the user account was created

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project_assignments = db.relationship('ProjectAssignment', backref='staff', lazy=True)
    driver_assignments = db.relationship('DriverVehicleAssignment', backref='driver', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='staff', lazy=True, cascade="all, delete-orphan")

    # Database Indexes for Performance
    __table_args__ = (
        db.Index('idx_staff_company', 'company_id'),
        db.Index('idx_staff_phone', 'personal_phone'),
        db.Index('idx_staff_email', 'personal_email'),
        db.Index('idx_staff_status', 'status'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "staff_id": self.staff_id,
            "name": (self.first_name or "") + " " + (self.last_name or ""),
            "phone": self.personal_phone,
            "email": self.personal_email,
            # Personal Information
            "first_name": self.first_name,
            "last_name": self.last_name,
            "father_name": self.father_name,
            "date_of_birth": self.date_of_birth.strftime('%Y-%m-%d') if self.date_of_birth else None,
            "gender": self.gender,
            # Contact Information
            "personal_email": self.personal_email,
            "personal_phone": self.personal_phone,
            "alternate_phone": self.alternate_phone,
            # Present Address
            "present_address": self.present_address,
            "present_city": self.present_city,
            "present_state": self.present_state,
            "present_pincode": self.present_pincode,
            # Permanent Address
            "permanent_address": self.permanent_address,
            "permanent_city": self.permanent_city,
            "permanent_state": self.permanent_state,
            "permanent_pincode": self.permanent_pincode,
            # Employment Details
            "designation": self.designation,
            "department": self.department,
            "role": self.role,
            "joining_date": self.joining_date.strftime('%Y-%m-%d') if self.joining_date else None,
            "employment_type": self.employment_type,
            # Qualifications
            "highest_qualification": self.highest_qualification,
            "specialization": self.specialization,
            "license_number": self.license_number,
            "license_expiry": self.license_expiry.strftime('%Y-%m-%d') if self.license_expiry else None,
            # Bank Details
            "bank_name": self.bank_name,
            "account_number": self.account_number,
            "ifsc_code": self.ifsc_code,
            "account_holder_name": self.account_holder_name,
            # Emergency Contact
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "emergency_contact_relation": self.emergency_contact_relation,
            # Financial Details
            "monthly_salary": self.monthly_salary,
            "ctc": self.ctc,
            "pf_applicable": self.pf_applicable,
            "pf_percentage": self.pf_percentage,
            "esi_applicable": self.esi_applicable,
            "esi_percentage": self.esi_percentage,
            "professional_tax_applicable": self.professional_tax_applicable,
            "professional_tax_amount": self.professional_tax_amount,
            "pan_number": self.pan_number,
            "income_tax_regime": self.income_tax_regime,
            # Status
            "status": self.status,
            "photo": self.photo,
            "user_id": self.user_id,
            "needs_user_access": self.needs_user_access,
            "user_created_at": self.user_created_at.strftime('%Y-%m-%d %H:%M:%S') if self.user_created_at else None,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def __repr__(self):
        return f"<Staff {self.first_name} {self.last_name}>"
