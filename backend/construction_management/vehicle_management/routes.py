
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from vehicle_management.models import Vehicle
from vehicle_management.fuel_log import FuelLog
from vehicle_management.maintenance import MaintenanceLog, MaintenanceSchedule
from vehicle_management.vehicle_project_assignment import VehicleProjectAssignment, VehicleProjectHistory
from vehicle_management.driver_assignment import DriverVehicleAssignment
from user_management.models import User
from staff_management.models import Staff
from project_management.models import Project
from finance_management.models.cash_transaction import CashTransaction
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import (
    success_response, error_response, paginated_response,
    server_error_response, not_found_response
)
from datetime import datetime

vehicle_bp = Blueprint("vehicle", __name__, url_prefix="/api/vehicles")


def parse_date(date_str):
    """Convert date string (YYYY-MM-DD) to date object or return None if empty"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@vehicle_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_vehicles():
    """Get all vehicles with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1 or per_page < 1:
            return error_response("Page and per_page must be positive integers", status_code=400)

        query = Vehicle.query.order_by(Vehicle.id.desc())
        paginated = query.paginate(page=page, per_page=per_page)

        return paginated_response(
            items=[v.to_dict() for v in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Vehicles retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>", methods=["GET"])
@jwt_required()
def get_vehicle(vehicle_id):
    """Get a single vehicle by ID"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"No vehicle with ID {vehicle_id} found")
        return success_response(vehicle.to_dict(), "Vehicle retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/", methods=["POST"])
@jwt_required()
def create_vehicle():
    """Create a new vehicle"""
    try:
        data = request.get_json()

        # Validate required fields
        errors = []
        if not data.get("make"):
            errors.append({"field": "make", "message": "Make is required"})
        if not data.get("model"):
            errors.append({"field": "model", "message": "Model is required"})
        if not data.get("year"):
            errors.append({"field": "year", "message": "Year is required"})
        if not data.get("registration_number"):
            errors.append({"field": "registration_number", "message": "Registration number is required"})
        if not data.get("type"):
            errors.append({"field": "type", "message": "Vehicle type is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Check if registration number already exists
        existing = Vehicle.query.filter_by(registration_number=data.get("registration_number")).first()
        if existing:
            return error_response(
                "Registration number already exists",
                details=f"A vehicle with registration {data.get('registration_number')} already exists",
                status_code=400
            )

        # Create new vehicle
        vehicle = Vehicle(
            make=data.get("make"),
            model=data.get("model"),
            year=int(data.get("year")),
            registration_number=data.get("registration_number"),
            mileage=float(data.get("mileage")) if data.get("mileage") else None,
            status=data.get("status", "active"),
            type=data.get("type"),
            registration_date=parse_date(data.get("registration_date")),
            pollution_date=parse_date(data.get("pollution_date")),
            insurance_date=parse_date(data.get("insurance_date")),
            tax_date=parse_date(data.get("tax_date")),
            geology_certificate_date=parse_date(data.get("geology_certificate_date")),
            emi_status=data.get("emi_status", False),
            emi_amount=float(data.get("emi_amount")) if data.get("emi_amount") else None
        )

        db.session.add(vehicle)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Vehicle',
            entity_id=vehicle.id,
            action='CREATE',
            new_values=vehicle.to_dict(),
            entity_name=vehicle.registration_number,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(vehicle.to_dict(), "Vehicle created successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>", methods=["PUT"])
@jwt_required()
def update_vehicle(vehicle_id):
    """Update an existing vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"No vehicle with ID {vehicle_id} found")

        # Capture old values BEFORE update
        old_values = vehicle.to_dict()

        data = request.get_json()

        # Check registration number uniqueness if being updated
        if "registration_number" in data and data["registration_number"] != vehicle.registration_number:
            existing = Vehicle.query.filter_by(registration_number=data.get("registration_number")).first()
            if existing:
                return error_response(
                    "Registration number already exists",
                    details=f"A vehicle with registration {data.get('registration_number')} already exists",
                    status_code=400
                )

        # Update fields
        if "make" in data:
            vehicle.make = data["make"]
        if "model" in data:
            vehicle.model = data["model"]
        if "year" in data:
            vehicle.year = int(data["year"])
        if "registration_number" in data:
            vehicle.registration_number = data["registration_number"]
        if "mileage" in data:
            vehicle.mileage = float(data["mileage"]) if data["mileage"] else None
        if "status" in data:
            vehicle.status = data["status"]
        if "type" in data:
            vehicle.type = data["type"]
        if "registration_date" in data:
            vehicle.registration_date = parse_date(data["registration_date"])
        if "pollution_date" in data:
            vehicle.pollution_date = parse_date(data["pollution_date"])
        if "insurance_date" in data:
            vehicle.insurance_date = parse_date(data["insurance_date"])
        if "tax_date" in data:
            vehicle.tax_date = parse_date(data["tax_date"])
        if "geology_certificate_date" in data:
            vehicle.geology_certificate_date = parse_date(data["geology_certificate_date"])
        if "emi_status" in data:
            vehicle.emi_status = data["emi_status"]
        if "emi_amount" in data:
            vehicle.emi_amount = float(data["emi_amount"]) if data["emi_amount"] else None

        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Vehicle',
            entity_id=vehicle.id,
            action='UPDATE',
            old_values=old_values,
            new_values=vehicle.to_dict(),
            entity_name=vehicle.registration_number,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(vehicle.to_dict(), "Vehicle updated successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>", methods=["DELETE"])
@jwt_required()
def delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"No vehicle with ID {vehicle_id} found")

        # Capture data BEFORE delete
        deleted_data = vehicle.to_dict()
        vehicle_name = vehicle.registration_number

        db.session.delete(vehicle)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Vehicle',
            entity_id=vehicle_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=vehicle_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Vehicle deleted successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


# ==================== FUEL LOG ENDPOINTS ====================

@vehicle_bp.route("/<int:vehicle_id>/fuel-logs", methods=["POST"])
@jwt_required()
def create_fuel_log(vehicle_id):
    """Create a fuel log entry and auto-create Finance transaction"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        # Verify user's company has access to this vehicle
        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", details="Cannot access vehicle from different company", status_code=403)

        data = request.get_json()

        # Validate required fields
        errors = []
        if not data.get("date"):
            errors.append({"field": "date", "message": "Date is required"})
        if data.get("amount") is None or data.get("amount") <= 0:
            errors.append({"field": "amount", "message": "Amount (liters) must be greater than 0"})
        if data.get("cost") is None or data.get("cost") <= 0:
            errors.append({"field": "cost", "message": "Cost must be greater than 0"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Create fuel log
        fuel_log = FuelLog(
            vehicle_id=vehicle_id,
            project_id=data.get("project_id"),
            company_id=user.company_id,
            date=parse_date(data.get("date")),
            amount=float(data.get("amount")),
            cost=float(data.get("cost")),
            notes=data.get("notes"),
            created_by=int(user_id)
        )

        db.session.add(fuel_log)
        db.session.flush()  # Get the ID before creating transaction

        # Auto-create Finance transaction
        transaction = CashTransaction(
            project_id=fuel_log.project_id,
            date=fuel_log.date,
            type='expense',
            category='fuel',
            amount=fuel_log.cost,
            description=f"Fuel for {vehicle.registration_number}",
            created_by=int(user_id)
        )
        db.session.add(transaction)
        db.session.flush()

        # Link fuel log to transaction
        fuel_log.transaction_id = transaction.id
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='FuelLog',
            entity_id=fuel_log.id,
            action='CREATE',
            new_values=fuel_log.to_dict(),
            entity_name=f"Fuel - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(fuel_log.to_dict(), "Fuel log created successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/fuel-logs", methods=["GET"])
@jwt_required()
def get_fuel_logs(vehicle_id):
    """Get all fuel logs for a vehicle with pagination"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        # Verify access
        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1 or per_page < 1:
            return error_response("Page and per_page must be positive integers", status_code=400)

        query = FuelLog.query.filter_by(vehicle_id=vehicle_id).order_by(FuelLog.date.desc())
        paginated = query.paginate(page=page, per_page=per_page)

        return paginated_response(
            items=[f.to_dict() for f in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Fuel logs retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/fuel-logs/<int:log_id>", methods=["PUT"])
@jwt_required()
def update_fuel_log(vehicle_id, log_id):
    """Update a fuel log entry"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        fuel_log = FuelLog.query.get(log_id)
        if not fuel_log or fuel_log.vehicle_id != vehicle_id:
            return not_found_response("FuelLog", details=f"Fuel log {log_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if fuel_log.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        old_values = fuel_log.to_dict()
        data = request.get_json()

        # Update fields
        if "date" in data:
            fuel_log.date = parse_date(data["date"])
        if "amount" in data:
            fuel_log.amount = float(data["amount"])
        if "cost" in data:
            fuel_log.cost = float(data["cost"])
        if "notes" in data:
            fuel_log.notes = data["notes"]

        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='FuelLog',
            entity_id=fuel_log.id,
            action='UPDATE',
            old_values=old_values,
            new_values=fuel_log.to_dict(),
            entity_name=f"Fuel - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(fuel_log.to_dict(), "Fuel log updated successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/fuel-logs/<int:log_id>", methods=["DELETE"])
@jwt_required()
def delete_fuel_log(vehicle_id, log_id):
    """Delete a fuel log"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        fuel_log = FuelLog.query.get(log_id)
        if not fuel_log or fuel_log.vehicle_id != vehicle_id:
            return not_found_response("FuelLog", details=f"Fuel log {log_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if fuel_log.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        old_values = fuel_log.to_dict()

        # Also delete associated transaction if exists
        if fuel_log.transaction_id:
            CashTransaction.query.filter_by(id=fuel_log.transaction_id).delete()

        db.session.delete(fuel_log)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='FuelLog',
            entity_id=log_id,
            action='DELETE',
            old_values=old_values,
            entity_name=f"Fuel - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Fuel log deleted successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/fuel-logs/summary", methods=["GET"])
@jwt_required()
def get_fuel_summary(vehicle_id):
    """Get fuel consumption summary for a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        # Query fuel logs
        fuel_logs = FuelLog.query.filter_by(vehicle_id=vehicle_id).all()

        total_liters = sum(f.amount for f in fuel_logs)
        total_cost = sum(f.cost for f in fuel_logs)
        avg_liters = total_liters / len(fuel_logs) if fuel_logs else 0
        avg_cost_per_liter = total_cost / total_liters if total_liters > 0 else 0

        summary = {
            'vehicle_id': vehicle_id,
            'total_liters': round(total_liters, 2),
            'total_cost': round(total_cost, 2),
            'average_liters_per_log': round(avg_liters, 2),
            'average_cost_per_liter': round(avg_cost_per_liter, 2),
            'log_count': len(fuel_logs)
        }

        return success_response(summary, "Fuel summary retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))


# ==================== MAINTENANCE LOG ENDPOINTS ====================

@vehicle_bp.route("/<int:vehicle_id>/maintenance-logs", methods=["POST"])
@jwt_required()
def create_maintenance_log(vehicle_id):
    """Create a maintenance log entry and auto-create Finance transaction"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        data = request.get_json()

        # Validate required fields
        errors = []
        if not data.get("date"):
            errors.append({"field": "date", "message": "Date is required"})
        if not data.get("type"):
            errors.append({"field": "type", "message": "Maintenance type is required"})
        if data.get("cost") is None or data.get("cost") <= 0:
            errors.append({"field": "cost", "message": "Cost must be greater than 0"})
        if not data.get("description"):
            errors.append({"field": "description", "message": "Description is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Create maintenance log
        maintenance_log = MaintenanceLog(
            vehicle_id=vehicle_id,
            company_id=user.company_id,
            date=parse_date(data.get("date")),
            type=data.get("type"),
            cost=float(data.get("cost")),
            description=data.get("description"),
            service_center=data.get("service_center"),
            mileage_at_service=float(data.get("mileage_at_service")) if data.get("mileage_at_service") else None,
            created_by=int(user_id)
        )

        db.session.add(maintenance_log)
        db.session.flush()

        # Auto-create Finance transaction
        transaction = CashTransaction(
            date=maintenance_log.date,
            type='expense',
            category='maintenance',
            amount=maintenance_log.cost,
            description=f"Maintenance for {vehicle.registration_number}: {maintenance_log.type}",
            created_by=int(user_id)
        )
        db.session.add(transaction)
        db.session.flush()

        maintenance_log.transaction_id = transaction.id
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='MaintenanceLog',
            entity_id=maintenance_log.id,
            action='CREATE',
            new_values=maintenance_log.to_dict(),
            entity_name=f"Maintenance - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(maintenance_log.to_dict(), "Maintenance log created successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/maintenance-logs", methods=["GET"])
@jwt_required()
def get_maintenance_logs(vehicle_id):
    """Get all maintenance logs for a vehicle with pagination"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1 or per_page < 1:
            return error_response("Page and per_page must be positive integers", status_code=400)

        query = MaintenanceLog.query.filter_by(vehicle_id=vehicle_id).order_by(MaintenanceLog.date.desc())
        paginated = query.paginate(page=page, per_page=per_page)

        return paginated_response(
            items=[m.to_dict() for m in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Maintenance logs retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/maintenance-logs/<int:log_id>", methods=["PUT"])
@jwt_required()
def update_maintenance_log(vehicle_id, log_id):
    """Update a maintenance log entry"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        maintenance_log = MaintenanceLog.query.get(log_id)
        if not maintenance_log or maintenance_log.vehicle_id != vehicle_id:
            return not_found_response("MaintenanceLog", details=f"Maintenance log {log_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if maintenance_log.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        old_values = maintenance_log.to_dict()
        data = request.get_json()

        # Update fields
        if "date" in data:
            maintenance_log.date = parse_date(data["date"])
        if "type" in data:
            maintenance_log.type = data["type"]
        if "cost" in data:
            maintenance_log.cost = float(data["cost"])
        if "description" in data:
            maintenance_log.description = data["description"]
        if "service_center" in data:
            maintenance_log.service_center = data["service_center"]
        if "mileage_at_service" in data:
            maintenance_log.mileage_at_service = float(data["mileage_at_service"]) if data["mileage_at_service"] else None

        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='MaintenanceLog',
            entity_id=maintenance_log.id,
            action='UPDATE',
            old_values=old_values,
            new_values=maintenance_log.to_dict(),
            entity_name=f"Maintenance - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(maintenance_log.to_dict(), "Maintenance log updated successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/maintenance-logs/<int:log_id>", methods=["DELETE"])
@jwt_required()
def delete_maintenance_log(vehicle_id, log_id):
    """Delete a maintenance log"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        maintenance_log = MaintenanceLog.query.get(log_id)
        if not maintenance_log or maintenance_log.vehicle_id != vehicle_id:
            return not_found_response("MaintenanceLog", details=f"Maintenance log {log_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if maintenance_log.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        old_values = maintenance_log.to_dict()

        # Also delete associated transaction if exists
        if maintenance_log.transaction_id:
            CashTransaction.query.filter_by(id=maintenance_log.transaction_id).delete()

        db.session.delete(maintenance_log)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='MaintenanceLog',
            entity_id=log_id,
            action='DELETE',
            old_values=old_values,
            entity_name=f"Maintenance - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Maintenance log deleted successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


# ==================== MAINTENANCE SCHEDULE ENDPOINTS ====================

@vehicle_bp.route("/<int:vehicle_id>/maintenance-schedule", methods=["POST"])
@jwt_required()
def create_maintenance_schedule(vehicle_id):
    """Create a maintenance schedule for preventive maintenance"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        data = request.get_json()

        # Validate
        errors = []
        if not data.get("maintenance_type"):
            errors.append({"field": "maintenance_type", "message": "Maintenance type is required"})
        if data.get("interval_km") and data.get("interval_km") <= 0:
            errors.append({"field": "interval_km", "message": "Interval KM must be greater than 0"})
        if data.get("interval_days") and data.get("interval_days") <= 0:
            errors.append({"field": "interval_days", "message": "Interval days must be greater than 0"})

        if not data.get("interval_km") and not data.get("interval_days"):
            errors.append({"field": "intervals", "message": "At least one interval (KM or days) is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        schedule = MaintenanceSchedule(
            vehicle_id=vehicle_id,
            company_id=user.company_id,
            maintenance_type=data.get("maintenance_type"),
            interval_km=float(data.get("interval_km")) if data.get("interval_km") else None,
            interval_days=int(data.get("interval_days")) if data.get("interval_days") else None,
            last_done_km=float(data.get("last_done_km")) if data.get("last_done_km") else None,
            last_done_date=parse_date(data.get("last_done_date")) if data.get("last_done_date") else None,
            next_due_km=float(data.get("next_due_km")) if data.get("next_due_km") else None,
            next_due_date=parse_date(data.get("next_due_date")) if data.get("next_due_date") else None,
            created_by=int(user_id)
        )

        db.session.add(schedule)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='MaintenanceSchedule',
            entity_id=schedule.id,
            action='CREATE',
            new_values=schedule.to_dict(),
            entity_name=f"Schedule - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(schedule.to_dict(), "Maintenance schedule created successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/maintenance-schedule", methods=["GET"])
@jwt_required()
def get_maintenance_schedules(vehicle_id):
    """Get all maintenance schedules for a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        schedules = MaintenanceSchedule.query.filter_by(vehicle_id=vehicle_id).all()

        return success_response(
            [s.to_dict() for s in schedules],
            "Maintenance schedules retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/maintenance-schedule/<int:schedule_id>", methods=["PUT"])
@jwt_required()
def update_maintenance_schedule(vehicle_id, schedule_id):
    """Update a maintenance schedule"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        schedule = MaintenanceSchedule.query.get(schedule_id)
        if not schedule or schedule.vehicle_id != vehicle_id:
            return not_found_response("MaintenanceSchedule", details=f"Schedule {schedule_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if schedule.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        old_values = schedule.to_dict()
        data = request.get_json()

        # Update fields
        if "maintenance_type" in data:
            schedule.maintenance_type = data["maintenance_type"]
        if "interval_km" in data:
            schedule.interval_km = float(data["interval_km"]) if data["interval_km"] else None
        if "interval_days" in data:
            schedule.interval_days = int(data["interval_days"]) if data["interval_days"] else None
        if "last_done_km" in data:
            schedule.last_done_km = float(data["last_done_km"]) if data["last_done_km"] else None
        if "last_done_date" in data:
            schedule.last_done_date = parse_date(data["last_done_date"]) if data["last_done_date"] else None
        if "next_due_km" in data:
            schedule.next_due_km = float(data["next_due_km"]) if data["next_due_km"] else None
        if "next_due_date" in data:
            schedule.next_due_date = parse_date(data["next_due_date"]) if data["next_due_date"] else None

        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='MaintenanceSchedule',
            entity_id=schedule.id,
            action='UPDATE',
            old_values=old_values,
            new_values=schedule.to_dict(),
            entity_name=f"Schedule - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(schedule.to_dict(), "Maintenance schedule updated successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/maintenance-schedule/<int:schedule_id>", methods=["DELETE"])
@jwt_required()
def delete_maintenance_schedule(vehicle_id, schedule_id):
    """Delete a maintenance schedule"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        schedule = MaintenanceSchedule.query.get(schedule_id)
        if not schedule or schedule.vehicle_id != vehicle_id:
            return not_found_response("MaintenanceSchedule", details=f"Schedule {schedule_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if schedule.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        old_values = schedule.to_dict()

        db.session.delete(schedule)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='MaintenanceSchedule',
            entity_id=schedule_id,
            action='DELETE',
            old_values=old_values,
            entity_name=f"Schedule - {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Maintenance schedule deleted successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/maintenance-due", methods=["GET"])
@jwt_required()
def get_all_maintenance_due():
    """Get all vehicles with due maintenance (company-wide)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        schedules = MaintenanceSchedule.query.filter_by(company_id=user.company_id).all()
        due_maintenance = []

        for schedule in schedules:
            vehicle = Vehicle.query.get(schedule.vehicle_id)
            if schedule.is_due(vehicle.mileage or 0):
                due_maintenance.append({
                    'schedule': schedule.to_dict(),
                    'vehicle': vehicle.to_dict(),
                    'due_by_km': schedule.is_due_by_km(vehicle.mileage or 0),
                    'due_by_date': schedule.is_due_by_date()
                })

        return success_response(due_maintenance, "Maintenance due items retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))


# ==================== VEHICLE-PROJECT ASSIGNMENT ENDPOINTS ====================

@vehicle_bp.route("/<int:vehicle_id>/assign-project", methods=["POST"])
@jwt_required()
def assign_vehicle_to_project(vehicle_id):
    """Assign a vehicle to a project"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        data = request.get_json()

        # Validate
        errors = []
        if not data.get("project_id"):
            errors.append({"field": "project_id", "message": "Project ID is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        project_id = int(data.get("project_id"))
        project = Project.query.get(project_id)
        if not project or project.company_id != user.company_id:
            return not_found_response("Project", details=f"Project {project_id} not found or inaccessible")

        # Check for duplicate active assignment
        existing = VehicleProjectAssignment.query.filter_by(
            vehicle_id=vehicle_id,
            project_id=project_id,
            removed_on=None
        ).first()

        if existing:
            return error_response(
                "Vehicle already assigned to this project",
                details=f"Vehicle is already assigned to project {project_id}",
                status_code=400
            )

        # Create assignment
        assignment = VehicleProjectAssignment(
            project_id=project_id,
            vehicle_id=vehicle_id,
            company_id=user.company_id,
            notes=data.get("notes"),
            created_by=int(user_id)
        )

        # Also create history record
        history = VehicleProjectHistory(
            project_id=project_id,
            vehicle_id=vehicle_id,
            company_id=user.company_id,
            assigned_date=datetime.utcnow(),
            notes=data.get("notes"),
            created_by=int(user_id)
        )

        db.session.add(assignment)
        db.session.add(history)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='VehicleProjectAssignment',
            entity_id=assignment.id,
            action='CREATE',
            new_values=assignment.to_dict(),
            entity_name=f"{vehicle.registration_number} -> Project {project_id}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(assignment.to_dict(), "Vehicle assigned to project successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/unassign-project", methods=["POST"])
@jwt_required()
def unassign_vehicle_from_project(vehicle_id):
    """Remove a vehicle from a project (soft delete)"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        data = request.get_json()

        # Validate
        if not data.get("project_id"):
            return error_response("Validation failed", errors=[{"field": "project_id", "message": "Project ID is required"}], status_code=400)

        project_id = int(data.get("project_id"))

        # Find assignment
        assignment = VehicleProjectAssignment.query.filter_by(
            vehicle_id=vehicle_id,
            project_id=project_id,
            removed_on=None
        ).first()

        if not assignment:
            return not_found_response("Assignment", details=f"No active assignment found for vehicle {vehicle_id} to project {project_id}")

        old_values = assignment.to_dict()

        # Soft delete: set removed_on timestamp
        assignment.removed_on = datetime.utcnow()

        # Update history record
        history = VehicleProjectHistory.query.filter_by(
            vehicle_id=vehicle_id,
            project_id=project_id,
            unassigned_date=None
        ).first()

        if history:
            history.unassigned_date = datetime.utcnow()

        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='VehicleProjectAssignment',
            entity_id=assignment.id,
            action='UPDATE',
            old_values=old_values,
            new_values=assignment.to_dict(),
            entity_name=f"{vehicle.registration_number} <- Project {project_id}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Vehicle unassigned from project successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/projects", methods=["GET"])
@jwt_required()
def get_vehicle_projects(vehicle_id):
    """Get all projects (active and inactive) for a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        assignments = VehicleProjectAssignment.query.filter_by(vehicle_id=vehicle_id).all()

        return success_response(
            [a.to_dict() for a in assignments],
            "Vehicle projects retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/projects/active", methods=["GET"])
@jwt_required()
def get_vehicle_active_projects(vehicle_id):
    """Get only currently active projects for a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        assignments = VehicleProjectAssignment.query.filter_by(
            vehicle_id=vehicle_id,
            removed_on=None
        ).all()

        return success_response(
            [a.to_dict() for a in assignments],
            "Active projects retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/assignment-history", methods=["GET"])
@jwt_required()
def get_vehicle_assignment_history(vehicle_id):
    """Get full audit trail of vehicle-project assignments"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        history = VehicleProjectHistory.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleProjectHistory.assigned_date.desc()).all()

        return success_response(
            [h.to_dict() for h in history],
            "Assignment history retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))


# ==================== DRIVER ASSIGNMENT ENDPOINTS ====================

@vehicle_bp.route("/<int:vehicle_id>/assign-driver", methods=["POST"])
@jwt_required()
def assign_driver_to_vehicle(vehicle_id):
    """Assign a driver (staff member) to a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        data = request.get_json()

        # Validate
        errors = []
        if not data.get("driver_id"):
            errors.append({"field": "driver_id", "message": "Driver ID is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        driver_id = int(data.get("driver_id"))
        driver = Staff.query.get(driver_id)
        if not driver or driver.company_id != user.company_id:
            return not_found_response("Staff", details=f"Driver {driver_id} not found or inaccessible")

        # Check for duplicate active assignment
        existing = DriverVehicleAssignment.query.filter_by(
            vehicle_id=vehicle_id,
            unassigned_date=None
        ).first()

        if existing:
            return error_response(
                "Vehicle already has an active driver",
                details=f"Vehicle is already assigned to driver {existing.driver_id}",
                status_code=400
            )

        # Create assignment
        assignment = DriverVehicleAssignment(
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            company_id=user.company_id,
            notes=data.get("notes"),
            created_by=int(user_id)
        )

        db.session.add(assignment)
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='DriverVehicleAssignment',
            entity_id=assignment.id,
            action='CREATE',
            new_values=assignment.to_dict(),
            entity_name=f"{driver.name} -> {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(assignment.to_dict(), "Driver assigned to vehicle successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/unassign-driver", methods=["POST"])
@jwt_required()
def unassign_driver_from_vehicle(vehicle_id):
    """Remove a driver from a vehicle (soft delete)"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        # Find active assignment
        assignment = DriverVehicleAssignment.query.filter_by(
            vehicle_id=vehicle_id,
            unassigned_date=None
        ).first()

        if not assignment:
            return not_found_response("Assignment", details=f"No active driver assignment found for vehicle {vehicle_id}")

        old_values = assignment.to_dict()
        driver = Staff.query.get(assignment.driver_id)

        # Soft delete: set unassigned_date timestamp
        assignment.unassigned_date = datetime.utcnow()
        db.session.commit()

        # Log activity
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='DriverVehicleAssignment',
            entity_id=assignment.id,
            action='UPDATE',
            old_values=old_values,
            new_values=assignment.to_dict(),
            entity_name=f"{driver.name} <- {vehicle.registration_number}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Driver unassigned from vehicle successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/driver", methods=["GET"])
@jwt_required()
def get_vehicle_current_driver(vehicle_id):
    """Get the current driver assigned to a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        assignment = DriverVehicleAssignment.query.filter_by(
            vehicle_id=vehicle_id,
            unassigned_date=None
        ).first()

        if not assignment:
            return success_response(None, "No active driver assigned to this vehicle")

        driver = Staff.query.get(assignment.driver_id)

        return success_response({
            'assignment': assignment.to_dict(),
            'driver': driver.to_dict() if driver else None
        }, "Current driver retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))


@vehicle_bp.route("/<int:vehicle_id>/driver-history", methods=["GET"])
@jwt_required()
def get_vehicle_driver_history(vehicle_id):
    """Get full assignment history of drivers for a vehicle"""
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return not_found_response("Vehicle", details=f"Vehicle with ID {vehicle_id} not found")

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if vehicle.company_id != user.company_id:
            return error_response("Unauthorized", status_code=403)

        assignments = DriverVehicleAssignment.query.filter_by(vehicle_id=vehicle_id).order_by(DriverVehicleAssignment.assigned_date.desc()).all()

        result = []
        for assignment in assignments:
            driver = Staff.query.get(assignment.driver_id)
            result.append({
                'assignment': assignment.to_dict(),
                'driver': driver.to_dict() if driver else None
            })

        return success_response(result, "Driver history retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))
