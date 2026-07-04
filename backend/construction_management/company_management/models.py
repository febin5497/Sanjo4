from extensions import db

# NOTE: This model is DEPRECATED - use company_settings.models.Company instead
# Keeping this file for backward compatibility but the model is disabled
# to avoid table definition conflicts with company_settings.models.Company

# DO NOT USE - This is deprecated
# class Company(db.Model):
#     __tablename__ = "companies"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     created_at = db.Column(db.DateTime, server_default=db.func.now())