import os
import re

BASE_DIR = "."

errors = []
warnings = []


def check_routes():

    for root, dirs, files in os.walk(BASE_DIR):

        for file in files:

            if file == "routes.py":

                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                if "@jwt_required()" not in content:

                    warnings.append(
                        f"{path} → API without authentication"
                    )


def check_models():

    for root, dirs, files in os.walk(BASE_DIR):

        for file in files:

            if file == "models.py":

                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                if "db.Model" not in content:

                    warnings.append(
                        f"{path} → no SQLAlchemy models detected"
                    )


def check_foreign_keys():

    pattern = r"ForeignKey\(['\"](\w+)\."

    for root, dirs, files in os.walk(BASE_DIR):

        for file in files:

            if file.endswith(".py"):

                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                matches = re.findall(pattern, content)

                for table in matches:

                    found = False

                    for r, d, fs in os.walk(BASE_DIR):

                        for f2 in fs:

                            if f2 == "models.py":

                                with open(os.path.join(r, f2), "r", encoding="utf-8") as mf:

                                    if f"class {table.capitalize()}" in mf.read():

                                        found = True

                    if not found:

                        errors.append(
                            f"{path} → ForeignKey refers to missing table '{table}'"
                        )


def check_init_files():

    for root, dirs, files in os.walk(BASE_DIR):

        if "__pycache__" in root:
            continue

        if root == ".":
            continue

        if "__init__.py" not in files:

            warnings.append(
                f"{root} → missing __init__.py"
            )


def run_scan():

    print("\nScanning backend project...\n")

    check_routes()
    check_models()
    check_foreign_keys()
    check_init_files()

    print("--------- ERRORS ---------")

    for e in errors:
        print(e)

    print("\n--------- WARNINGS ---------")

    for w in warnings:
        print(w)

    print("\nScan complete.")


if __name__ == "__main__":

    run_scan()