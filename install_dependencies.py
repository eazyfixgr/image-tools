"""
Image Resizer & Optimizer - Dependency Installer
This script installs all required packages for the Image Resizer application.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    print(f"\nInstalling {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}")
        print(f"Error: {e}")
        return False

def check_package(package_name):
    """Check if a package is already installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 60)
    print("Image Resizer & Optimizer - Dependency Installer")
    print("=" * 60)
    print("\nThis script will install the following packages:")
    print("  - Pillow (Image processing)")
    print("  - tkinterdnd2 (Drag and drop support)")
    print("\n")

    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("Error: pip is not installed or not accessible")
        print("Please install pip first")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Upgrade pip first
    print("Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✓ pip upgraded successfully\n")
    except subprocess.CalledProcessError:
        print("Warning: Could not upgrade pip, continuing anyway...\n")

    # Packages to install
    packages = [
        ("PIL", "Pillow>=10.0.0"),
        ("tkinterdnd2", "tkinterdnd2>=0.3.0")
    ]

    # Check and install packages
    results = []
    for import_name, pip_package in packages:
        package_display = pip_package.split(">=")[0]

        if check_package(import_name):
            print(f"✓ {package_display} is already installed")
            results.append(True)
        else:
            results.append(install_package(pip_package))

    # Verify installation by checking again
    print("\n" + "=" * 60)
    print("Verifying Installation")
    print("=" * 60)

    verification_results = []
    for import_name, pip_package in packages:
        package_display = pip_package.split(">=")[0]
        if check_package(import_name):
            print(f"✓ {package_display} verified")
            verification_results.append(True)
        else:
            print(f"✗ {package_display} NOT FOUND")
            verification_results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("Installation Summary")
    print("=" * 60)

    success_count = sum(verification_results)
    total_count = len(verification_results)

    if success_count == total_count:
        print(f"\n✓ All packages installed successfully ({success_count}/{total_count})")
        print("\nYou can now run the Image Resizer application:")
        print("  Double-click 'run.bat' or run: python image_resizer.py")
    else:
        print(f"\n⚠ Some packages failed to install ({success_count}/{total_count})")
        print("\nTry one of these solutions:")
        print("  1. Double-click 'install_and_run.bat'")
        print("  2. Run: pip install Pillow tkinterdnd2")
        print("  3. Run: python -m pip install Pillow tkinterdnd2")

        print(f"\nPython executable: {sys.executable}")
        print(f"Python version: {sys.version}")

    print("\n" + "=" * 60)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
