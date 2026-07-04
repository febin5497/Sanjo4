from extensions import db
from datetime import datetime


class TaskStaffAssignment(db.Model):
    """
    Model for assigning staff members to specific project tasks
    Supports multiple staff per task and tracks assignment history
    Uses soft-delete pattern (removed_on timestamp) for historical tracking
    """
    __tablename__ = 'task_staff_assignments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Assignment Tracking
    assigned_on = db.Column(db.DateTime, default=datetime.utcnow)
    removed_on = db.Column(db.DateTime, nullable=True)  # Soft delete for history tracking

    # Role and Metadata
    role_on_task = db.Column(db.String(100), nullable=True)  # Lead, Support, QA, etc.
    assigned_by_user_id = db.Column(db.Integer, nullable=True)  # Who made the assignment

    # Additional tracking
    hours_allocated = db.Column(db.Float, nullable=True)  # Estimated hours for this task
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    staff = db.relationship('Staff', backref='task_assignments', foreign_keys=[staff_id])
    # Note: task relationship is created via backref from ProjectTask.task_assignments

    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "staff_id": self.staff_id,
            "staff_name": f"{self.staff.first_name} {self.staff.last_name}" if self.staff else None,
            "staff_role": self.staff.role if self.staff else None,
            "assigned_on": self.assigned_on.strftime('%Y-%m-%d %H:%M') if self.assigned_on else None,
            "removed_on": self.removed_on.strftime('%Y-%m-%d %H:%M') if self.removed_on else None,
            "role_on_task": self.role_on_task,
            "hours_allocated": self.hours_allocated,
            "notes": self.notes,
            "is_active": self.removed_on is None
        }

    def to_gantt_staff_dict(self):
        """Convert to Gantt chart staff assignment format"""
        return {
            "id": self.id,
            "staff_name": f"{self.staff.first_name} {self.staff.last_name}" if self.staff else "Unknown",
            "assigned_on": self.assigned_on.strftime('%Y-%m-%d') if self.assigned_on else None,
            "role": self.role_on_task or "Team Member",
            "hours_allocated": self.hours_allocated
        }
