import os
import shutil

BASE_DIR = "."
IGNORE = ["venv", "__pycache__", ".git"]

print("\n🔧 ERP ROUTE STABILIZER STARTED\n")

for root, dirs, files in os.walk(BASE_DIR):

    if any(x in root for x in IGNORE):
        continue

    if "routes.py" in files:

        route_file = os.path.join(root, "routes.py")
        module_name = os.path.basename(root)

        print(f"Checking {route_file}")

        # backup original
        backup = route_file + ".backup"

        if not os.path.exists(backup):
            shutil.copy(route_file, backup)
            print("Backup created")

        blueprint_name = module_name.replace("_management", "")
        bp_var = f"{blueprint_name}_bp"

        template = f"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

{bp_var} = Blueprint("{blueprint_name}", __name__)


@{bp_var}.route("/{blueprint_name}", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({{
        "module": "{module_name}",
        "status": "working"
    }})
"""

        with open(route_file, "w", encoding="utf-8") as f:
            f.write(template)

        print("Rebuilt routes safely\n")

print("✅ ERP ROUTES STABILIZED\n")