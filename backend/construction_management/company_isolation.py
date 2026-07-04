import os
import re

BASE_DIR = "."

def update_query_all(line):

    pattern = r'(\w+)\.query\.all\(\)'
    match = re.search(pattern, line)

    if match:

        model = match.group(1)

        return f"{model}.query.filter_by(company_id=user.company_id).all()\n"

    return line


def update_query_get(line):

    pattern = r'(\w+)\.query\.get\((.+)\)'
    match = re.search(pattern, line)

    if match:

        model = match.group(1)
        param = match.group(2)

        return f"""{model}.query.filter_by(
    id={param},
    company_id=user.company_id
).first()
"""

    return line


def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    modified = False

    for line in lines:

        updated = update_query_all(line)
        updated = update_query_get(updated)

        if updated != line:
            modified = True

        new_lines.append(updated)

    if modified:

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print("SECURED:", filepath)


def scan_project():

    for root, dirs, files in os.walk(BASE_DIR):

        for file in files:

            if file == "routes.py":

                process_file(os.path.join(root, file))


if __name__ == "__main__":

    print("Applying company isolation security...\n")

    scan_project()

    print("\nSecurity update complete.")