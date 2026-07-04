from extensions import db
from datetime import datetime
from client_management.models import Client


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    location = db.Column(db.String(120), nullable=False)

    start_date = db.Column(db.Date, nullable=False)

    user_id = db.Column(db.Integer, nullable=False)

    # Multi-company support
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)

    # financial fields
    rate_per_sqft = db.Column(db.Float, nullable=True)

    square_feet = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(50), default="Not Started")

    # documents
    agreement = db.Column(db.String(255), nullable=True)

    plan = db.Column(db.String(255), nullable=True)

    three_d_plan = db.Column(db.String(255), nullable=True)

    panchayat_certificate = db.Column(db.String(255), nullable=True)

    # geographic coordinates
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # client relation
    client_id = db.Column(
        db.Integer,
        db.ForeignKey('clients.id'),
        nullable=False
    )

    # staff history
    staff_history = db.relationship(
        'ProjectStaffHistory',
        backref='project',
        lazy=True,
        cascade="all, delete-orphan"
    )

    project_assignments = db.relationship(
        'ProjectAssignment',
        backref='project',
        lazy=True,
        cascade="all, delete-orphan"
    )

    # Database Indexes for Performance
    __table_args__ = (
        db.Index('idx_project_company', 'company_id'),
        db.Index('idx_project_client', 'client_id'),
        db.Index('idx_project_status', 'status'),
        db.Index('idx_project_user', 'user_id'),
    )

    def to_dict(self):

        return {

            "id": self.id,

            "name": self.name,

            "location": self.location,

            "start_date": self.start_date,

            "user_id": self.user_id,

            "rate_per_sqft": self.rate_per_sqft,

            "square_feet": self.square_feet,

            "status": self.status,

            "client_id": self.client_id,

            "client": self.client.name if self.client else None,

            "latitude": self.latitude,
            "longitude": self.longitude,

            "documents": {

                "Agreement": self.agreement,

                "PLAN": self.plan,

                "3D Plan": self.three_d_plan,

                "Panchayat Certificate": self.panchayat_certificate

            }

        }


class ProjectStaffHistory(db.Model):

    __tablename__ = 'project_staff_history'

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id'),
        nullable=False
    )

    staff_id = db.Column(db.Integer, nullable=False)

    assigned_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    unassigned_date = db.Column(
        db.DateTime,
        nullable=True
    )