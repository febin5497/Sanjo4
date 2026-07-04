from extensions import db
from datetime import datetime


class ProjectLocation(db.Model):
    __tablename__ = "project_locations"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(255))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text)
    marker_type = db.Column(db.String(50), default="project")
    marker_color = db.Column(db.String(20), default="#0052CC")
    description = db.Column(db.Text)
    is_gate = db.Column(db.Boolean, default=False)
    is_entry_point = db.Column(db.Boolean, default=False)
    radius_meters = db.Column(db.Float, default=50.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship("Project", backref=db.backref("locations", lazy="dynamic"))

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "marker_type": self.marker_type,
            "marker_color": self.marker_color,
            "description": self.description,
            "is_gate": self.is_gate,
            "is_entry_point": self.is_entry_point,
            "radius_meters": self.radius_meters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
