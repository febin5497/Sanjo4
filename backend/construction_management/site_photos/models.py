from extensions import db
from datetime import datetime


class SitePhoto(db.Model):
    __tablename__ = "site_photos"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    photo_path = db.Column(db.String(500), nullable=False)
    thumbnail_path = db.Column(db.String(500))
    caption = db.Column(db.String(255))
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default="general")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    taken_at = db.Column(db.DateTime)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship("Project", backref=db.backref("site_photos", lazy="dynamic"))
    uploader = db.relationship("User", backref=db.backref("uploaded_photos", lazy="dynamic"))

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "photo_path": self.photo_path,
            "thumbnail_path": self.thumbnail_path,
            "caption": self.caption,
            "description": self.description,
            "category": self.category,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "taken_at": self.taken_at.isoformat() if self.taken_at else None,
            "uploaded_by": self.uploaded_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
