import subprocess
import sys
import bpy

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False
    return True

def check_and_install_dependencies():
    packages = ["openai", "numpy"]
    installed = True

    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            success = install_package(package)
            if success:
                print(f"{package} installed successfully.")
            else:
                installed = False
                print(f"Failed to install {package}.")
    
    if not installed:
        bpy.ops.ui.show_message_box(message="Some dependencies failed to install. Check the Blender console for details.")
