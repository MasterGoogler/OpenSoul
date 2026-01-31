"""
install_prereqs.py

Installs required Python packages for OpenSoul agents and users.
Run: python install_prereqs.py
"""
import subprocess
import sys

REQUIRED_PACKAGES = [
    "bsv-sdk",
    "requests"
]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    for pkg in REQUIRED_PACKAGES:
        print(f"Installing {pkg}...")
        install(pkg)
    print("All required packages installed.")
