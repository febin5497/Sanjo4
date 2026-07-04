from extensions import db
from datetime import datetime


class PlannerTask(db.Model):
    """Task model for project planning/Gantt chart"""
    __tablename__ = 'planner_tasks'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='todo')  # todo, in-progress, done
    progress = db.Column(db.Integer, default=0)  # 0-100
    dependencies = db.Column(db.String(255), nullable=True)  # JSON string of task IDs
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert task to dictionary for API responses"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'task_name': self.task_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'progress': self.progress,
            'dependencies': self.dependencies,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<PlannerTask {self.id}: {self.task_name}>'
