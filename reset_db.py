import os
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "dev.db")
MIGRATIONS_PATH = os.path.join(BASE_DIR, "migrations")

def run(cmd):
    print(f"\n▶ Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

def main():
    print("🔥 RESETTING DATABASE (PYTHON MODE)")

    # 1. Delete DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("✅ Deleted dev.db")
    else:
        print("ℹ️ dev.db not found")

    # 2. Delete migrations
    if os.path.exists(MIGRATIONS_PATH):
        shutil.rmtree(MIGRATIONS_PATH)
        print("✅ Deleted migrations folder")
    else:
        print("ℹ️ migrations folder not found")

    # 3. Recreate migrations
    run("flask db init")
    run('flask db migrate -m "initial schema"')
    run("flask db upgrade")

    print("\n🎉 DATABASE RESET COMPLETE")
    print("You should see: Running upgrade -> head")

if __name__ == "__main__":
    main()
