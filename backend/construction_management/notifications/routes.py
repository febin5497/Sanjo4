
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime, timedelta
from .models import Notification

notifications_bp = Blueprint("notifications", __name__)


# Get all notifications for current user
@notifications_bp.route("/api/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()

        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        query = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc())

        if unread_only:
            query = query.filter_by(is_read=False)

        total = query.count()
        notifications = query.limit(limit).offset(offset).all()

        return jsonify({
            'success': True,
            'data': [n.to_dict() for n in notifications],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Get unread notification count
@notifications_bp.route("/api/notifications/unread-count", methods=["GET"])
@jwt_required()
def get_unread_count():
    try:
        user_id = get_jwt_identity()
        count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

        return jsonify({
            'success': True,
            'unread_count': count
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Mark notification as read
@notifications_bp.route("/api/notifications/<int:notification_id>/read", methods=["PUT"])
@jwt_required()
def mark_as_read(notification_id):
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'data': notification.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Mark all notifications as read
@notifications_bp.route("/api/notifications/mark-all-read", methods=["PUT"])
@jwt_required()
def mark_all_as_read():
    try:
        user_id = get_jwt_identity()
        Notification.query.filter_by(user_id=user_id, is_read=False).update(
            {'is_read': True, 'read_at': datetime.utcnow()}
        )
        db.session.commit()

        return jsonify({'success': True, 'message': 'All notifications marked as read'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Delete notification
@notifications_bp.route("/api/notifications/<int:notification_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notification_id):
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404

        db.session.delete(notification)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Notification deleted'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Clear all notifications
@notifications_bp.route("/api/notifications/clear-all", methods=["DELETE"])
@jwt_required()
def clear_all_notifications():
    try:
        user_id = get_jwt_identity()
        Notification.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        return jsonify({'success': True, 'message': 'All notifications cleared'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Register FCM token for push notifications (mobile)
@notifications_bp.route("/api/notifications/register-fcm", methods=["POST"])
@jwt_required()
def register_fcm_token():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        fcm_token = data.get('fcm_token')

        if not fcm_token:
            return jsonify({'success': False, 'error': 'FCM token required'}), 400

        # For now, we just store it with a notification
        # In production, you would use Firebase Admin SDK to send notifications

        return jsonify({
            'success': True,
            'message': 'FCM token registered',
            'fcm_token': fcm_token
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Create notification (internal use)
def create_notification(user_id, company_id, title, message, notification_type, related_model=None, related_id=None):
    """
    Helper function to create notifications
    Called from other modules when events occur
    """
    try:
        notification = Notification(
            user_id=user_id,
            company_id=company_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_model=related_model,
            related_id=related_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {str(e)}")
        return None


# Health check
@notifications_bp.route("/api/notifications/health", methods=["GET"])
def health_check():
    return jsonify({
        "module": "notifications",
        "status": "working"
    }), 200
