# purchase_management/routes/__init__.py
from .procurement_routes import procurement_bp

# Import purchase_bp from the parent routes.py file
# We use importlib to avoid naming conflicts with the routes/ package
import importlib.util
import os
parent_routes_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'routes.py')
spec = importlib.util.spec_from_file_location("purchase_routes", parent_routes_path)
purchase_routes_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(purchase_routes_module)
purchase_bp = purchase_routes_module.purchase_bp
