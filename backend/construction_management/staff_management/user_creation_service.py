"""
User Account Automation Service
Automatically creates user accounts when staff is created
"""

import secrets
import string
from extensions import db
from user_management.models import User
from staff_management.user_id_service import UserIDGenerator
from datetime import datetime

class UserCreationService:
    """Service for automatically creating user accounts for staff"""

    DEFAULT_PASSWORD = "Erp@123"

    @staticmethod
    def generate_password(length=12):
        """
        Return the default password for all new users.
        Users are required to change this on first login.

        Returns:
            str: The default password
        """
        return UserCreationService.DEFAULT_PASSWORD

    @staticmethod
    def create_user_for_staff(staff_data, company_id):
        """
        Create a user account for a new staff member

        Args:
            staff_data (dict): Staff data dictionary containing personal info
            company_id (int): The company ID

        Returns:
            tuple: (User object, user_id, default_password) or (None, None, None) on error
        """
        try:
            # Generate User ID
            user_id = UserIDGenerator.generate_user_id(company_id)

            # Generate default password
            default_password = UserCreationService.generate_password()

            # Determine user role based on staff role
            staff_role = staff_data.get('role', 'worker').lower()
            user_role = UserCreationService.map_staff_role_to_user_role(staff_role)

            # Create user account
            user = User(
                username=user_id,  # User ID as username
                name=f"{staff_data.get('first_name', '')} {staff_data.get('last_name', '')}".strip(),
                email=staff_data.get('personal_email'),
                role=user_role,
                company_id=company_id,
                is_active=True,
                password_change_required=True  # Force password change on first login
            )

            # Hash and set password
            user.set_password(default_password)

            # Add and commit to database
            db.session.add(user)
            db.session.flush()  # Flush to get the ID without committing

            return user, user_id, default_password

        except Exception as e:
            print(f"Error creating user account: {str(e)}")
            return None, None, None

    @staticmethod
    def map_staff_role_to_user_role(staff_role):
        """
        Map staff role to user role for permissions

        Args:
            staff_role (str): Staff role (manager, driver, site_engineer, supervisor, worker)

        Returns:
            str: User role for the system
        """
        role_mapping = {
            'manager': 'manager',
            'driver': 'driver',
            'site_engineer': 'site_engineer',
            'site engineer': 'site_engineer',
            'supervisor': 'supervisor',
            'worker': 'worker',
            'admin': 'admin'
        }

        return role_mapping.get(staff_role.lower(), 'worker')

    @staticmethod
    def update_staff_user_link(staff, user):
        """
        Link a staff record to a user account

        Args:
            staff: Staff object
            user: User object

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            staff.user_id = user.id
            staff.needs_user_access = True
            staff.user_created_at = datetime.utcnow()
            db.session.add(staff)
            return True
        except Exception as e:
            print(f"Error linking staff to user: {str(e)}")
            return False

    @staticmethod
    def deactivate_user_for_staff(staff):
        """
        Deactivate user account when staff is marked as inactive

        Args:
            staff: Staff object

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if staff.user_id:
                user = User.query.get(staff.user_id)
                if user:
                    user.is_active = False
                    db.session.add(user)
                    return True
            return False
        except Exception as e:
            print(f"Error deactivating user account: {str(e)}")
            return False

    @staticmethod
    def get_user_for_staff(staff):
        """
        Get the user account associated with a staff member

        Args:
            staff: Staff object

        Returns:
            User object or None
        """
        if staff.user_id:
            return User.query.get(staff.user_id)
        return None

    @staticmethod
    def reset_user_password(staff):
        """
        Reset a staff member's user password to the default.
        User must change on next login.

        Args:
            staff: Staff object

        Returns:
            tuple: (User object, new_password) or (None, None) on error
        """
        try:
            user = UserCreationService.get_user_for_staff(staff)
            if user:
                new_password = UserCreationService.DEFAULT_PASSWORD
                user.set_password(new_password)
                user.password_change_required = True
                db.session.add(user)
                return user, new_password
            return None, None
        except Exception as e:
            print(f"Error resetting user password: {str(e)}")
            return None, None
