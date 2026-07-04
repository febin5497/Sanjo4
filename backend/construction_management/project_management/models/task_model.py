from extensions import db
from datetime import datetime


class ProjectTask(db.Model):
    """
    Model for individual project tasks/milestones
    Tracks task details, progress, status, and staff assignments
    """
    __tablename__ = 'project_tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Task Details
    task_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(50), nullable=True)  # Milestone, Phase, Activity, Subtask

    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # Progress & Status
    status = db.Column(db.String(50), default='todo')  # todo, in-progress, done, blocked
    progress = db.Column(db.Float, default=0)  # 0-100 percentage

    # Ordering/Priority
    order_index = db.Column(db.Integer, default=0)  # For sorting within project
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = db.Column(db.Integer, nullable=True)

    # Relationships
    task_assignments = db.relationship(
        'TaskStaffAssignment',
        backref='task',
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys='TaskStaffAssignment.task_id'
    )

    # Foreign key relationships
    project = db.relationship('Project', backref='tasks', foreign_keys=[project_id])

    def to_dict(self):
        """Convert task to dictionary with all details"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "task_name": self.task_name,
            "description": self.description,
            "task_type": self.task_type,
            "start_date": self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            "end_date": self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            "status": self.status,
            "progress": self.progress,
            "priority": self.priority,
            "order_index": self.order_index,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else None,
            "assigned_staff_count": len([a for a in self.task_assignments if not a.removed_on]),
            "task_assignments": [a.to_dict() for a in self.task_assignments if not a.removed_on]
        }

    def to_gantt_dict(self):
        """Convert to Gantt chart format"""
        assigned_staff = [
            a.staff.first_name + ' ' + a.staff.last_name
            for a in self.task_assignments
            if not a.removed_on and a.staff
        ]

        return {
            "id": str(self.id),
            "name": self.task_name,
            "start": self.start_date.isoformat() if self.start_date else None,
            "end": self.end_date.isoformat() if self.end_date else None,
            "progress": self.progress,
            "type": "task",
            "project_id": self.project_id,
            "task_id": self.id,
            "status": self.status,
            "priority": self.priority,
            "description": self.description or "",
            "assigned_staff": ", ".join(assigned_staff) if assigned_staff else "Unassigned",
            "assigned_staff_list": assigned_staff,
            "isDisabled": self.status == "blocked"
        }
