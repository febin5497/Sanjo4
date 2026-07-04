from extensions import db
from datetime import datetime


class ProjectAssignment(db.Model):
    __tablename__ = "project_assignments"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

    assigned_on = db.Column(db.DateTime, default=datetime.utcnow)
    removed_on = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "staff_id": self.staff_id,
            "assigned_on": self.assigned_on.strftime('%Y-%m-%d %H:%M') if self.assigned_on else None,
            "removed_on": self.removed_on.strftime('%Y-%m-%d %H:%M') if self.removed_on else None,
        }
