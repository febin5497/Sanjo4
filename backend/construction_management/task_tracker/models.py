from extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default="Pending")  # Pending, In Progress, Done
    due_date = db.Column(db.String(50), nullable=True)

    # Optional foreign keys
    project_id = db.Column(db.Integer, nullable=True)
    assigned_to = db.Column(db.Integer, nullable=True)  # staff_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "due_date": self.due_date,
            "project_id": self.project_id,
            "assigned_to": self.assigned_to
        }
