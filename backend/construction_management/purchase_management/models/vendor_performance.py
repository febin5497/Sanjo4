from extensions import db
from datetime import datetime
from models.base import AuditMixin


class VendorPerformance(db.Model, AuditMixin):
    """Track vendor/supplier performance metrics"""
    __tablename__ = 'vendor_performance'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)

    # Performance metrics
    on_time_percentage = db.Column(db.Float, default=0, nullable=False)  # 0-100
    quality_score = db.Column(db.Float, default=0, nullable=False)  # 0-100
    overall_score = db.Column(db.Float, default=0, nullable=False)  # Weighted average

    # Notes and timestamp
    notes = db.Column(db.Text, nullable=True)
    recorded_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vendor = db.relationship('Supplier', backref='performance_records')

    def calculate_overall_score(self):
        """Calculate weighted overall score"""
        # 50% on-time, 50% quality
        self.overall_score = (self.on_time_percentage * 0.5) + (self.quality_score * 0.5)
        return self.overall_score

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'on_time_percentage': self.on_time_percentage,
            'quality_score': self.quality_score,
            'overall_score': self.overall_score,
            'notes': self.notes,
            'recorded_date': self.recorded_date.isoformat() if self.recorded_date else None,
        }
