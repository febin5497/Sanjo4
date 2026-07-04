"""
User ID Generation Service
Generates unique User IDs in format: STF-YYYY-SEQUENCE
Example: STF-2026-001, STF-2026-002, etc.
"""

from datetime import datetime
from extensions import db
from staff_management.models import Staff

class UserIDGenerator:
    """Service for generating unique User IDs for staff members"""

    @staticmethod
    def generate_user_id(company_id):
        """
        Generate a unique User ID for a staff member
        Format: STF-YYYY-SEQUENCE

        Args:
            company_id (int): The company ID for the staff member

        Returns:
            str: A unique User ID like "STF-2026-001"
        """
        current_year = datetime.now().year

        # Query for the highest sequence number for this company and year
        existing_staff = Staff.query.filter(
            Staff.company_id == company_id,
            Staff.staff_id.startswith(f"STF-{current_year}-")
        ).all()

        # Calculate next sequence number
        next_sequence = len(existing_staff) + 1

        # Format with leading zeros (001, 002, etc.)
        user_id = f"STF-{current_year}-{next_sequence:03d}"

        # Ensure uniqueness (in case of race conditions)
        while Staff.query.filter_by(staff_id=user_id).first():
            next_sequence += 1
            user_id = f"STF-{current_year}-{next_sequence:03d}"

        return user_id

    @staticmethod
    def get_next_sequence_number(company_id):
        """
        Get the next sequence number for a company in the current year

        Args:
            company_id (int): The company ID

        Returns:
            int: The next sequence number
        """
        current_year = datetime.now().year

        existing_staff = Staff.query.filter(
            Staff.company_id == company_id,
            Staff.staff_id.startswith(f"STF-{current_year}-")
        ).all()

        return len(existing_staff) + 1

    @staticmethod
    def extract_sequence_number(user_id):
        """
        Extract the sequence number from a User ID

        Args:
            user_id (str): User ID like "STF-2026-001"

        Returns:
            int: The sequence number (e.g., 1 for "STF-2026-001")
        """
        parts = user_id.split('-')
        if len(parts) == 3:
            try:
                return int(parts[2])
            except ValueError:
                return None
        return None

    @staticmethod
    def extract_year_from_user_id(user_id):
        """
        Extract the year from a User ID

        Args:
            user_id (str): User ID like "STF-2026-001"

        Returns:
            int: The year (e.g., 2026 for "STF-2026-001")
        """
        parts = user_id.split('-')
        if len(parts) == 3:
            try:
                return int(parts[1])
            except ValueError:
                return None
        return None
