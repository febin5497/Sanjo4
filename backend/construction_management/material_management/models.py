from extensions import db

class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit_of_measurement = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Float, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Adding created_at

    project = db.relationship('Project', backref=db.backref('materials', lazy=True))

    # Database Indexes for Performance
    __table_args__ = (
        db.Index('idx_material_project', 'project_id'),
        db.Index('idx_material_name', 'name'),
    )

    def __repr__(self):
        return f"<Material {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'unit_of_measurement': self.unit_of_measurement,
            'price': self.price,
            'project_id': self.project_id,
            'created_at': self.created_at  # Add created_at to the dictionary
        }
