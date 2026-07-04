"""
Initialize default roles and permissions for RBAC system.
This function should be called after db.create_all() to ensure tables exist.
"""

from extensions import db
from admin_management.models import Role, Permission


def init_default_permissions():
    """
    Create default permissions for the system.
    This is idempotent - it only creates permissions that don't already exist.
    """

    permissions_data = [
        # Projects Permissions
        ('read_projects', 'Projects', 'View all projects'),
        ('create_project', 'Projects', 'Create new project'),
        ('update_project', 'Projects', 'Update project details'),
        ('delete_project', 'Projects', 'Delete project'),
        ('manage_project_staff', 'Projects', 'Assign/unassign staff to projects'),

        # Staff Permissions
        ('read_staff', 'Staff', 'View staff list'),
        ('create_staff', 'Staff', 'Create new staff member'),
        ('update_staff', 'Staff', 'Update staff details'),
        ('delete_staff', 'Staff', 'Delete staff member'),
        ('approve_attendance', 'Staff', 'Approve staff attendance/punch-in photos'),
        ('manage_timesheets', 'Staff', 'Create and manage staff timesheets'),

        # Finance Permissions
        ('read_finance', 'Finance', 'View financial reports and data'),
        ('create_invoice', 'Finance', 'Create invoices'),
        ('update_invoice', 'Finance', 'Update invoices'),
        ('delete_invoice', 'Finance', 'Delete invoices'),
        ('approve_payment', 'Finance', 'Approve payments'),
        ('manage_transactions', 'Finance', 'Manage financial transactions'),

        # Materials & Inventory Permissions
        ('read_materials', 'Inventory', 'View materials inventory'),
        ('create_material', 'Inventory', 'Add new material to inventory'),
        ('update_material', 'Inventory', 'Update material details'),
        ('delete_material', 'Inventory', 'Delete material from inventory'),
        ('manage_purchases', 'Inventory', 'Manage material purchases'),
        ('manage_sales', 'Inventory', 'Manage material sales'),

        # Vehicles Permissions
        ('read_vehicles', 'Vehicles', 'View vehicle list'),
        ('create_vehicle', 'Vehicles', 'Add new vehicle'),
        ('update_vehicle', 'Vehicles', 'Update vehicle details'),
        ('delete_vehicle', 'Vehicles', 'Delete vehicle'),

        # Attendance Permissions
        ('read_attendance', 'Attendance', 'View attendance records'),
        ('create_attendance', 'Attendance', 'Create attendance entry'),
        ('update_attendance', 'Attendance', 'Update attendance'),

        # Documents Permissions
        ('read_documents', 'Documents', 'View documents'),
        ('upload_document', 'Documents', 'Upload documents'),
        ('delete_document', 'Documents', 'Delete documents'),

        # Admin Permissions
        ('manage_users', 'Admin', 'Create, edit, delete users'),
        ('manage_roles', 'Admin', 'Create and modify roles'),
        ('manage_permissions', 'Admin', 'Assign permissions to roles'),
        ('view_audit_logs', 'Admin', 'View activity logs and audit trail'),
        ('manage_company_settings', 'Admin', 'Manage company configuration and settings'),
        ('view_admin_dashboard', 'Admin', 'Access admin dashboard'),
    ]

    for perm_name, category, description in permissions_data:
        # Check if permission already exists
        existing = Permission.query.filter_by(name=perm_name).first()
        if not existing:
            permission = Permission(
                name=perm_name,
                category=category,
                description=description
            )
            db.session.add(permission)
            print(f"Created permission: {perm_name}")
        else:
            print(f"Permission already exists: {perm_name}")

    db.session.commit()


def init_default_roles():
    """
    Create default roles with appropriate permissions.
    This is idempotent - it only creates roles that don't already exist.
    """

    roles_data = {
        'Super Admin': {
            'description': 'Full system access - can manage all aspects of the system',
            'is_system_role': True,
            'permissions': []  # Empty means all permissions
        },
        'Company Admin': {
            'description': 'Full company access - can manage company settings and users',
            'is_system_role': True,
            'permissions': [
                'read_projects', 'create_project', 'update_project', 'delete_project', 'manage_project_staff',
                'read_staff', 'create_staff', 'update_staff', 'delete_staff',
                'read_finance', 'create_invoice', 'update_invoice', 'delete_invoice', 'approve_payment',
                'read_materials', 'create_material', 'update_material', 'delete_material',
                'read_vehicles', 'create_vehicle', 'update_vehicle', 'delete_vehicle',
                'manage_users', 'manage_roles', 'manage_permissions', 'manage_company_settings', 'view_audit_logs'
            ]
        },
        'Manager': {
            'description': 'Can manage projects, staff, and finances',
            'is_system_role': True,
            'permissions': [
                'read_projects', 'create_project', 'update_project', 'manage_project_staff',
                'read_staff', 'create_staff', 'update_staff', 'approve_attendance', 'manage_timesheets',
                'read_finance', 'create_invoice', 'update_invoice', 'approve_payment',
                'read_materials', 'manage_purchases', 'manage_sales',
                'read_vehicles', 'view_audit_logs'
            ]
        },
        'Supervisor': {
            'description': 'Can supervise staff, manage attendance, and view reports',
            'is_system_role': True,
            'permissions': [
                'read_projects', 'read_staff', 'approve_attendance', 'manage_timesheets',
                'read_finance', 'read_materials', 'read_vehicles', 'read_documents'
            ]
        },
        'Staff': {
            'description': 'Standard staff member - can view own projects and submit attendance',
            'is_system_role': True,
            'permissions': [
                'read_projects', 'read_materials', 'create_attendance', 'read_documents', 'upload_document'
            ]
        }
    }

    for role_name, role_info in roles_data.items():
        # Check if role already exists
        existing = Role.query.filter_by(name=role_name).first()
        if not existing:
            role = Role(
                name=role_name,
                description=role_info['description'],
                is_system_role=role_info['is_system_role']
            )

            # Add permissions to role
            if role_name == 'Super Admin':
                # Super Admin gets all permissions
                all_permissions = Permission.query.all()
                role.permissions = all_permissions
            else:
                # Other roles get specific permissions
                for perm_name in role_info['permissions']:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)

            db.session.add(role)
            print(f"Created role: {role_name}")
        else:
            print(f"Role already exists: {role_name}")

    db.session.commit()


def init_rbac_system():
    """
    Initialize the entire RBAC system with default permissions and roles.
    Should be called once after db.create_all().
    """
    print("\n=== Initializing RBAC System ===")

    # Initialize permissions first (roles depend on permissions)
    print("\n1. Initializing default permissions...")
    init_default_permissions()

    # Initialize roles (which reference permissions)
    print("\n2. Initializing default roles...")
    init_default_roles()

    # Assign Super Admin role to existing admin user
    print("\n3. Assigning Super Admin role to admin user...")
    try:
        from user_management.models import User
        from admin_management.models import UserRole, Role

        # Find the admin user
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            # Find the Super Admin role
            super_admin_role = Role.query.filter_by(name='Super Admin').first()
            if super_admin_role:
                # Check if admin already has this role
                existing_role = UserRole.query.filter_by(
                    user_id=admin_user.id,
                    role_id=super_admin_role.id
                ).first()

                if not existing_role:
                    # Assign Super Admin role to admin user
                    user_role = UserRole(
                        user_id=admin_user.id,
                        role_id=super_admin_role.id
                    )
                    db.session.add(user_role)
                    db.session.commit()
                    print(f"Assigned Super Admin role to admin user")
                else:
                    print(f"Admin user already has Super Admin role")
            else:
                print("Super Admin role not found!")
        else:
            print("Admin user not found!")
    except Exception as e:
        print(f"Error assigning roles to admin user: {str(e)}")
        db.session.rollback()

    print("\n=== RBAC System Initialization Complete ===\n")
