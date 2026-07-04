def get_dashboard_data():
    total_projects = Project.query.count()
    total_staff = Staff.query.count()
    return {
        "projects": total_projects,
        "staff": total_staff
    }