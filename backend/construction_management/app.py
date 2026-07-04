import logging
import os
from flask import Flask, jsonify, send_from_directory, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_mail import Mail

from config import Config
from extensions import db, bcrypt, migrate


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    app.strict_slashes = False
    app.url_map.strict_slashes = False

    # CORS - Apply to ALL routes using configuration from environment variables
    CORS(
        app,
        resources={r"/api/.*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Request-ID"],
            "expose_headers": ["Content-Type", "Authorization", "X-Request-ID"],
            "supports_credentials": False,
            "max_age": 3600
        }},
        intercept_exceptions=False
    )

    # Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Import models AFTER db.init_app() so SQLAlchemy is properly initialized
    import user_management.models
    import company_settings.models  # This has the complete Company model
    # NOTE: Removed company_management.models to avoid duplicate Company table definition
    import staff_management.models
    import staff_management.expense_model
    import project_management.models.models
    import project_management.models.project_assignment
    import project_management.models.task_model
    import project_management.models.task_assignment
    import material_management.models
    import attendance_management.models
    import document_management.models
    import planner_management.models
    # Import finance models through the module import (no need for explicit class imports)
    import finance_management.models
    # Import vehicle management models (including new ones for fuel, maintenance, assignments)
    import vehicle_management.models
    import vehicle_management.fuel_log
    import vehicle_management.maintenance
    import vehicle_management.vehicle_project_assignment
    import vehicle_management.driver_assignment
    # Import payroll models
    import payroll_management.models
    # Import new inventory modules
    import supplier_management.models
    import purchase_management.models
    import purchase_returns.models
    import sales_management.models
    import sales_returns.models
    # Import admin management (RBAC, Activity Logging, Company Settings)
    import admin_management.models
    # Import notifications
    import notifications.models
    # Import equipment and quote management
    import equipment_management.models
    import quote_management.models
    # Import site photos and location mapping models
    import site_photos.models
    import location_mapping.models

    JWTManager(app)

    Mail(app)

    # Handle preflight requests (OPTIONS)
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200

    # Setup centralized error handling
    from middleware.error_handler import setup_error_handlers
    setup_error_handlers(app)

    register_blueprints(app)

    # Serve uploaded files
    @app.route("/uploads/projects/<int:project_id>/<filename>")
    def serve_uploaded_document(project_id, filename):
        upload_folder = os.path.join("uploads", "projects", str(project_id))
        return send_from_directory(upload_folder, filename)

    # Serve static files (logos, images, etc.)
    @app.route("/static/<filename>")
    def serve_static(filename):
        return send_from_directory("static", filename)

    # Root
    @app.route("/")
    def home():
        return jsonify({
            "message": "Construction Management API running"
        })

    # Health check endpoints
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/api/health")
    def api_health():
        return jsonify({"status": "ok"}), 200

    # Protected example - verify JWT and return user info
    @app.route("/api/protected")
    @jwt_required()
    def protected():
        current_user_id = get_jwt_identity()
        user = user_management.models.User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "company_id": user.company_id
            }
        }), 200

    return app


def register_blueprints(app):

    from auth.auth import auth_bp
    from staff_management.routes import staff_bp
    from vehicle_management.routes import vehicle_bp
    from material_management.routes import material_bp
    from finance_management.routes import finance_bp
    from finance_management.routes.approval_routes import approval_bp
    from finance_management.routes.budget_routes import budget_bp
    from finance_management.routes.coa_routes import coa_bp
    from finance_management.routes.retention_routes import retention_bp
    from finance_management.routes.reporting_routes import reporting_bp
    from finance_management.routes.stage_billing_routes import stage_billing_bp
    from dashboard.routes import dashboard_bp
    from document_management.routes import document_bp
    from task_tracker.routes import task_tracker_bp
    from project_management.routes.routes import project_bp
    from project_management.routes.task_routes import task_bp
    from project_management.routes.stage_routes import stage_bp
    from client_management.routes import client_bp
    from attendance_management.routes import attendance_bp
    from company_settings.routes import company_settings_bp
    from planner_management.routes import planner_bp
    # Admin management (RBAC, activity logging)
    from admin_management.routes.admin_routes import admin_bp
    # Payroll management
    from payroll_management.routes import payroll_bp
    # New inventory management modules
    from supplier_management.routes import supplier_bp
    from purchase_management.routes import purchase_bp
    from purchase_management.routes.procurement_routes import procurement_bp
    from purchase_management.routes.vendor_routes import vendor_bp
    from purchase_returns.routes import purchase_return_bp
    from sales_management.routes import sales_bp
    from sales_returns.routes import sales_return_bp
    # Invoice generator
    from invoice_generator.routes.routes import invoice_bp
    # Notifications
    from notifications.routes import notifications_bp
    # Equipment and Quote Management
    from equipment_management.routes import equipment_bp
    from quote_management.routes import quote_bp
    # Error Logging
    from error_logging.client_logs import client_logs_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(staff_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(material_bp)
    app.register_blueprint(finance_bp, url_prefix="/api/finance")
    app.register_blueprint(approval_bp, url_prefix="/api/finance")
    app.register_blueprint(budget_bp, url_prefix="/api/finance")
    app.register_blueprint(coa_bp, url_prefix="/api/finance")
    app.register_blueprint(retention_bp, url_prefix="/api/finance")
    app.register_blueprint(reporting_bp, url_prefix="/api/finance")
    app.register_blueprint(stage_billing_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(task_tracker_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(stage_bp)
    # NOTE: attendance_bp (explicit routes) registered via register_all_resource_routers
    # along with BaseResourceRouter-based CRUD endpoints
    app.register_blueprint(client_bp, url_prefix="/clients")
    app.register_blueprint(company_settings_bp, url_prefix="/api/company")
    app.register_blueprint(planner_bp)

    # Register admin management blueprint (RBAC, activity logging)
    app.register_blueprint(admin_bp)

    # Register payroll management blueprint
    app.register_blueprint(payroll_bp, url_prefix="/api/payroll")

    # Register inventory management blueprints
    app.register_blueprint(supplier_bp)
    app.register_blueprint(vendor_bp, url_prefix="/api")
    # NOTE: purchase_bp and procurement_bp (old explicit routes) disabled - using BaseResourceRouter routers instead
    # app.register_blueprint(purchase_bp)
    # app.register_blueprint(procurement_bp, url_prefix="/api/procurement")
    app.register_blueprint(purchase_return_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(sales_return_bp)

    # Register invoice generator blueprint
    app.register_blueprint(invoice_bp)

    # Register notifications blueprint
    app.register_blueprint(notifications_bp)

    # Register equipment and quote management blueprints
    app.register_blueprint(equipment_bp)
    app.register_blueprint(quote_bp)

    # Register error logging blueprint
    app.register_blueprint(client_logs_bp)

    # ==================== Phase 2.2: Register BaseResourceRouter Routers ====================
    # Auto-generated CRUD endpoints for 14 resource types (90+ endpoints total)
    from base.register_resource_routers import register_all_resource_routers
    register_all_resource_routers(app)

    print("\n[OK] Phase 2.2 Resource Routers Registered (14 routers, 90+ endpoints)")


# Logging
logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Run app
app = create_app()

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        # Initialize RBAC system with default roles and permissions
        from admin_management.init_defaults import init_rbac_system
        init_rbac_system()

        print("\nRegistered Routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.rule} -> {', '.join(rule.methods)}")

        print("\n")

    app.run(debug=False, host="0.0.0.0", port=5000)