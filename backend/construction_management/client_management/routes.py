
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from client_management.models import Client
from utils.response_formatter import (
    success_response, error_response, server_error_response, not_found_response
)

client_bp = Blueprint("client", __name__, url_prefix="/clients")


@client_bp.route("/", methods=["GET"])
@jwt_required()
def list_clients():
    try:
        clients = Client.query.order_by(Client.name).all()
        return success_response([c.to_dict() for c in clients], "Clients retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))


@client_bp.route("/<int:client_id>", methods=["GET"])
@jwt_required()
def get_client(client_id):
    try:
        client = Client.query.get(client_id)
        if not client:
            return not_found_response("Client", details=f"No client with ID {client_id} found")
        return success_response(client.to_dict(), "Client retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))


@client_bp.route("/", methods=["POST"])
@jwt_required()
def create_client():
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()

        errors = []
        if not name:
            errors.append({"field": "name", "message": "Name is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        client = Client(
            name=name,
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
        )
        db.session.add(client)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Client',
            entity_id=client.id,
            action='CREATE',
            new_values=client.to_dict(),
            entity_name=client.name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(client.to_dict(), "Client created successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@client_bp.route("/<int:client_id>", methods=["PUT"])
@jwt_required()
def update_client(client_id):
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        client = Client.query.get(client_id)
        if not client:
            return not_found_response("Client", details=f"No client with ID {client_id} found")

        # Capture old values BEFORE update
        old_values = client.to_dict()

        data = request.get_json(silent=True) or {}

        if "name" in data:
            client.name = data["name"].strip()
        if "email" in data:
            client.email = data["email"]
        if "phone" in data:
            client.phone = data["phone"]
        if "address" in data:
            client.address = data["address"]

        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Client',
            entity_id=client.id,
            action='UPDATE',
            old_values=old_values,
            new_values=client.to_dict(),
            entity_name=client.name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(client.to_dict(), "Client updated successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))


@client_bp.route("/<int:client_id>", methods=["DELETE"])
@jwt_required()
def delete_client(client_id):
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        client = Client.query.get(client_id)
        if not client:
            return not_found_response("Client", details=f"No client with ID {client_id} found")

        # Capture data BEFORE delete
        deleted_data = client.to_dict()
        client_name = client.name

        db.session.delete(client)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Client',
            entity_id=client_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=client_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Client deleted successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))
