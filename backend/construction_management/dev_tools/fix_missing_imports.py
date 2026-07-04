import os
import re

APP_FILE = "app.py"

print("\n🔎 Scanning app.py for broken imports...\n")

with open(APP_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
removed = []

for line in lines:

    match = re.match(r"\s*import\s+([a-zA-Z0-9_\.]+)", line)

    if match:

        module = match.group(1)
        module_path = module.replace(".", os.sep) + ".py"

        if not os.path.exists(module_path):

            removed.append(module)
            continue

    new_lines.append(line)

with open(APP_FILE, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ Broken imports removed:\n")

for r in removed:
    print("❌", r)

print("\n✔ app.py cleaned successfully\n")