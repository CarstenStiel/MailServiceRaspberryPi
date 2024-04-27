"""
Script to set up a virtual environment and set up service using configured settings.
"""

import subprocess
import os
import sys

def create_venv(venv_dir):
    """
    Create a virtual environment.

    Args:
        venv_dir (str): Directory path where the virtual environment will be created.
    """
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    except subprocess.CalledProcessError as e:
        print("Error creating virtual environment:", e)
        sys.exit(1)


def install_requirements(venv_dir, requirements_file):
    """
    Install Python dependencies from the requirements file inside the virtual environment.

    Args:
        venv_dir (str): Directory path of the virtual environment.
        requirements_file (str): Path to the requirements.txt file.
    """
    pip_path = os.path.join(venv_dir, "bin", "pip") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "pip.exe")
    try:
        subprocess.run([pip_path, "install", "-r", requirements_file], check=True)
    except subprocess.CalledProcessError as e:
        print("Error installing dependencies:", e)
        sys.exit(1)


if __name__ == "__main__":

    # Determine the path to the directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Path to the requirements.txt file
    requirements_file = os.path.join(script_dir, 'requirements.txt')

    # Path to the directory where the virtual environment will be created
    venv_dir = os.path.join(script_dir, '.venv')

    # Create virtual environment
    create_venv(venv_dir)

    # Install dependencies inside virtual environment
    install_requirements(venv_dir, requirements_file)

    # Activate the virtual environment
    # "nt" -> Windows and "posix" -> Linux or Mac
    activate_script = "Scripts\\activate.bat" if os.name == "nt" else "bin/activate"
    activate_shell = os.path.join(venv_dir, activate_script)
    try:
        args = [activate_shell] if os.name == "nt" else [".", activate_script]
        subprocess.run(args, shell=True, check=True)
        print("Virtual Environment activated.")
    except subprocess.CalledProcessError as e:
        print("Error activating virtual environment:", e)
        sys.exit(1)

    # Continue script execution within the virtual environment context

    # Additional code here, within the virtual environment context
    # For example:
    from src.System.DataCollector import DataCollector
    from src.System.Service import Service

    # System Variables
    data_collector = DataCollector()
    operating_system = data_collector.get_operating_system()
    service = Service(script_dir)

    # Service setup
    if operating_system == "Linux" or operating_system == "Raspberry":
        if not service.check_file_exists("/etc/systemd/system", "info-mail.service"):
            service.setLinuxService()
    else:
        print("Service for Windows is not implemented yet, but you can try the mail sending.")
