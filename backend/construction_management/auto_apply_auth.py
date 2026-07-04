import os

BASE_DIR = "."

TARGET_DECORATOR = "@jwt_required()"
ROLE_LINE = '    user = require_role(["admin","manager"])\n\n    if isinstance(user, tuple):\n        return user\n\n'

IMPORT_LINE = "from middleware.auth_middleware import require_role\n"


def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False

    # Add import if missing
    if IMPORT_LINE not in "".join(lines):
        for i, line in enumerate(lines):
            if "import" in line:
                lines.insert(i+1, IMPORT_LINE)
                modified = True
                break

    # Add middleware logic
    new_lines = []
    for i, line in enumerate(lines):

        new_lines.append(line)

        if TARGET_DECORATOR in line:

            # Look ahead to function definition
            if i + 1 < len(lines) and "def " in lines[i+1]:

                new_lines.append(lines[i+1])
                new_lines.append(ROLE_LINE)

                modified = True
                continue

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"UPDATED: {filepath}")


def scan_project():

    for root, dirs, files in os.walk(BASE_DIR):

        for file in files:

            if file == "routes.py":

                process_file(os.path.join(root, file))


if __name__ == "__main__":

    print("Applying authorization middleware to all route files...\n")

    scan_project()

    print("\nDone.")