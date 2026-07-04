"""
Unit Tests for ProjectTask and TaskStaffAssignment Models
Tests model creation, validation, relationships, and serialization
"""

import pytest
from datetime import datetime, date, timedelta
from app import create_app
from extensions import db
from project_management.models.task_model import ProjectTask
from project_management.models.task_assignment import TaskStaffAssignment
from staff_management.models import Staff
from project_management.models.models import Project
from user_management.models import User
from company_settings.models import Company


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def setup_data(app):
    """Create test data"""
    with app.app_context():
        # Create company
        company = Company(company_name="Test Company", registration_number="TC001")
        db.session.add(company)
        db.session.commit()

        # Create project
        project = Project(
            project_name="Test Project",
            company_id=company.id,
            status="Active",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        db.session.add(project)
        db.session.commit()

        # Create staff members
        staff1 = Staff(
            first_name="John",
            last_name="Doe",
            role="Developer",
            company_id=company.id,
            personal_email="john@example.com"
        )
        staff2 = Staff(
            first_name="Jane",
            last_name="Smith",
            role="Manager",
            company_id=company.id,
            personal_email="jane@example.com"
        )
        db.session.add_all([staff1, staff2])
        db.session.commit()

        # Create user for created_by
        user = User(
            username="testuser",
            email="test@example.com",
            company_id=company.id,
            role="admin"
        )
        db.session.add(user)
        db.session.commit()

        return {
            'company': company,
            'project': project,
            'staff1': staff1,
            'staff2': staff2,
            'user': user
        }


class TestProjectTaskModel:
    """Tests for ProjectTask model"""

    def test_project_task_creation(self, app, setup_data):
        """Test creating a project task"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Build API",
                description="Create REST API endpoints",
                task_type="Activity",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=5),
                status="todo",
                progress=0,
                priority="high",
                created_by_user_id=data['user'].id
            )
            db.session.add(task)
            db.session.commit()

            assert task.id is not None
            assert task.task_name == "Build API"
            assert task.status == "todo"
            assert task.progress == 0

    def test_project_task_defaults(self, app, setup_data):
        """Test default values for ProjectTask"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Test Task",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            assert task.status == "todo"
            assert task.progress == 0
            assert task.priority == "medium"
            assert task.order_index == 0

    def test_project_task_validation(self, app, setup_data):
        """Test task date validation"""
        with app.app_context():
            data = setup_data
            # End date before start date - should still create but be invalid logically
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Invalid Task",
                start_date=date.today() + timedelta(days=5),
                end_date=date.today(),  # Before start
                status="todo",
                progress=0
            )
            db.session.add(task)
            db.session.commit()

            # Model doesn't validate, but application logic should
            assert task.start_date > task.end_date

    def test_project_task_status_values(self, app, setup_data):
        """Test all valid status values"""
        with app.app_context():
            data = setup_data
            statuses = ["todo", "in-progress", "done", "blocked"]

            for status in statuses:
                task = ProjectTask(
                    project_id=data['project'].id,
                    company_id=data['company'].id,
                    task_name=f"Task {status}",
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=1),
                    status=status
                )
                db.session.add(task)
                db.session.commit()
                assert task.status == status

    def test_project_task_priority_values(self, app, setup_data):
        """Test all priority levels"""
        with app.app_context():
            data = setup_data
            priorities = ["low", "medium", "high", "critical"]

            for priority in priorities:
                task = ProjectTask(
                    project_id=data['project'].id,
                    company_id=data['company'].id,
                    task_name=f"Priority {priority}",
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=1),
                    priority=priority
                )
                db.session.add(task)
                db.session.commit()
                assert task.priority == priority

    def test_project_task_to_dict(self, app, setup_data):
        """Test task serialization to dictionary"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Serialize Test",
                description="Test serialization",
                task_type="Milestone",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=10),
                status="in-progress",
                progress=50,
                priority="high",
                order_index=1,
                created_by_user_id=data['user'].id
            )
            db.session.add(task)
            db.session.commit()

            task_dict = task.to_dict()

            assert task_dict['task_name'] == "Serialize Test"
            assert task_dict['description'] == "Test serialization"
            assert task_dict['status'] == "in-progress"
            assert task_dict['progress'] == 50
            assert task_dict['priority'] == "high"
            assert 'id' in task_dict
            assert 'start_date' in task_dict
            assert 'end_date' in task_dict

    def test_project_task_to_gantt_dict(self, app, setup_data):
        """Test Gantt chart serialization"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Gantt Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=5),
                progress=75,
                status="done",
                priority="medium"
            )
            db.session.add(task)
            db.session.commit()

            gantt_dict = task.to_gantt_dict()

            assert gantt_dict['name'] == "Gantt Test"
            assert gantt_dict['progress'] == 75
            assert gantt_dict['status'] == "done"

    def test_project_task_progress_range(self, app, setup_data):
        """Test progress value ranges"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Progress Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1),
                progress=100
            )
            db.session.add(task)
            db.session.commit()

            assert task.progress >= 0 and task.progress <= 100

    def test_project_task_relationships(self, app, setup_data):
        """Test relationships to other models"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Relationship Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            # Test project relationship
            assert task.project_id == data['project'].id
            assert task.company_id == data['company'].id
            assert task.staff_assignments is not None


class TestTaskStaffAssignmentModel:
    """Tests for TaskStaffAssignment model"""

    def test_task_staff_assignment_creation(self, app, setup_data):
        """Test creating a task staff assignment"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Test Task",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=5)
            )
            db.session.add(task)
            db.session.commit()

            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id,
                role_on_task="Lead",
                hours_allocated=40,
                assigned_by_user_id=data['user'].id
            )
            db.session.add(assignment)
            db.session.commit()

            assert assignment.id is not None
            assert assignment.task_id == task.id
            assert assignment.staff_id == data['staff1'].id
            assert assignment.removed_on is None

    def test_soft_delete_pattern(self, app, setup_data):
        """Test soft delete using removed_on timestamp"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Soft Delete Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id,
                assigned_by_user_id=data['user'].id
            )
            db.session.add(assignment)
            db.session.commit()

            # Soft delete
            assignment.removed_on = datetime.utcnow()
            db.session.commit()

            # Check record still exists but marked as removed
            retrieved = TaskStaffAssignment.query.get(assignment.id)
            assert retrieved is not None
            assert retrieved.removed_on is not None

    def test_assignment_to_dict(self, app, setup_data):
        """Test assignment serialization"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Serialize Assignment",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=5)
            )
            db.session.add(task)
            db.session.commit()

            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id,
                role_on_task="Developer",
                hours_allocated=30,
                assigned_by_user_id=data['user'].id
            )
            db.session.add(assignment)
            db.session.commit()

            assignment_dict = assignment.to_dict()

            assert assignment_dict['task_id'] == task.id
            assert assignment_dict['staff_id'] == data['staff1'].id
            assert assignment_dict['role_on_task'] == "Developer"
            assert assignment_dict['hours_allocated'] == 30
            assert assignment_dict['is_active'] == True

    def test_assignment_to_gantt_staff_dict(self, app, setup_data):
        """Test Gantt staff assignment serialization"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Gantt Staff Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id,
                role_on_task="Lead",
                hours_allocated=40
            )
            db.session.add(assignment)
            db.session.commit()

            gantt_dict = assignment.to_gantt_staff_dict()

            assert 'staff_name' in gantt_dict
            assert gantt_dict['role'] == "Lead"
            assert gantt_dict['hours_allocated'] == 40

    def test_multiple_assignments_per_task(self, app, setup_data):
        """Test assigning multiple staff to one task"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Multi-assign Task",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=5)
            )
            db.session.add(task)
            db.session.commit()

            # Assign two staff members
            assignment1 = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id,
                assigned_by_user_id=data['user'].id
            )
            assignment2 = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff2'].id,
                company_id=data['company'].id,
                assigned_by_user_id=data['user'].id
            )
            db.session.add_all([assignment1, assignment2])
            db.session.commit()

            # Query active assignments
            active_assignments = TaskStaffAssignment.query.filter(
                TaskStaffAssignment.task_id == task.id,
                TaskStaffAssignment.removed_on == None
            ).all()

            assert len(active_assignments) == 2

    def test_assignment_timestamps(self, app, setup_data):
        """Test assignment timestamp tracking"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Timestamp Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            before_assign = datetime.utcnow()
            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id,
                assigned_by_user_id=data['user'].id
            )
            db.session.add(assignment)
            db.session.commit()
            after_assign = datetime.utcnow()

            assert before_assign <= assignment.assigned_on <= after_assign
            assert assignment.removed_on is None


class TestTaskStaffAssignmentFiltering:
    """Tests for filtering and querying assignments"""

    def test_active_assignments_filter(self, app, setup_data):
        """Test filtering active assignments (removed_on is None)"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="Filter Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            # Create and remove an assignment
            assignment1 = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id
            )
            assignment2 = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff2'].id,
                company_id=data['company'].id
            )
            db.session.add_all([assignment1, assignment2])
            db.session.commit()

            # Remove one assignment
            assignment1.removed_on = datetime.utcnow()
            db.session.commit()

            # Query only active
            active = TaskStaffAssignment.query.filter(
                TaskStaffAssignment.task_id == task.id,
                TaskStaffAssignment.removed_on == None
            ).all()

            assert len(active) == 1
            assert active[0].staff_id == data['staff2'].id

    def test_assignment_history_retention(self, app, setup_data):
        """Test that soft-deleted assignments are retained"""
        with app.app_context():
            data = setup_data
            task = ProjectTask(
                project_id=data['project'].id,
                company_id=data['company'].id,
                task_name="History Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=data['staff1'].id,
                company_id=data['company'].id
            )
            db.session.add(assignment)
            db.session.commit()

            assignment_id = assignment.id
            assignment.removed_on = datetime.utcnow()
            db.session.commit()

            # Record should still exist with removed_on set
            record = TaskStaffAssignment.query.get(assignment_id)
            assert record is not None
            assert record.removed_on is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
