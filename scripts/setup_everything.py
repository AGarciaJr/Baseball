import subprocess
import sys
import os

# Automatically use the Python from the current venv
venv_python = os.path.join(sys.prefix, "Scripts", "python.exe")

scripts = [
    #"import_schema.py",
    #"link_pitchers_to_existing_no_hitters.py",
    #"make_admin.py",
    #"reset_passwords.py",
    "generate_trivia.py",
]

for script in scripts:
    print(f"Running {script}...")
    result = subprocess.run([venv_python, f"scripts/{script}"])
    if result.returncode != 0:
        print(f"❌ Error running {script}, aborting.")
        break
    print(f"✅ {script} completed.\n")

