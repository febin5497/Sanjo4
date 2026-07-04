from extensions import db
from datetime import datetime
from models.base import AuditMixin
from constants.statuses import PayrollCycleStatus

class PayrollCycle(db.Model, AuditMixin):
    __tablename__ = 'payroll_cycles'
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default=PayrollCycleStatus.DRAFT.value, nullable=False)  # draft, calculated, approved, paid
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    records = db.relationship('PayrollRecord', cascade='all, delete-orphan', backref='cycle')

    def to_dict(self):
        return {
            'id': self.id, 'month': self.month, 'year': self.year, 'status': self.status,
            'start_date': self.start_date.isoformat(), 'end_date': self.end_date.isoformat(),
            'approved_by_id': self.approved_by_id, 'company_id': self.company_id,
            'created_at': self.created_at.isoformat(), 'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id, 'updated_by_id': self.updated_by_id
        }

class PayrollRecord(db.Model):
    __tablename__ = 'payroll_records'
    id = db.Column(db.Integer, primary_key=True)
    cycle_id = db.Column(db.Integer, db.ForeignKey('payroll_cycles.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    days_worked = db.Column(db.Float, default=0)
    gross_salary = db.Column(db.Float, nullable=False)
    pf_amount = db.Column(db.Float, default=0)
    esi_amount = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    other_deductions = db.Column(db.Float, default=0)
    net_salary = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'cycle_id': self.cycle_id, 'staff_id': self.staff_id,
            'days_worked': self.days_worked, 'gross': self.gross_salary,
            'pf': self.pf_amount, 'esi': self.esi_amount, 'tax': self.tax_amount,
            'net': self.net_salary
        }
