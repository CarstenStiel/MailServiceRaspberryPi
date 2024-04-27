"""
Example script for setting up and activating a virtual environment and sending an email.

Please execute before the setup.py, to check if everything is working properly.
"""

import subprocess
import os
import sys

from src.Mail.Sender import MailSender


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
        print("\n")
    except subprocess.CalledProcessError as e:
        print("Error installing dependencies:", e)
        sys.exit(1)


def read_config(filename):
    """
    Reads the configuration file and loads the settings.

    Args:
        filename (str): The path to the configuration file.

    Returns:
        dict: A dictionary containing the loaded settings.
    """
    config = {}
    with open(filename, 'r') as file:
        exec(file.read(), config)
    return config


if __name__ == "__main__":

    # Get the directory path where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Path to the requirements.txt file
    requirements_file = os.path.join(script_dir, 'requirements.txt')

    # Path to the directory where the virtual environment will be created
    venv_dir = os.path.join(script_dir, '.venv')

    # Create the virtual environment
    create_venv(venv_dir)

    # Install dependencies inside the virtual environment
    install_requirements(venv_dir, requirements_file)

    # Activate the virtual environment
    activate_script = "Scripts\\activate.bat" if os.name == "nt" else "bin/activate"
    activate_shell = os.path.join(venv_dir, activate_script)
    try:
        args = [activate_shell] if os.name == "nt" else [".", activate_script]
        subprocess.run(args, shell=True, check=True)
        print("Virtual Environment activated.")
    except subprocess.CalledProcessError as e:
        print("Error activating virtual environment:", e)
        sys.exit(1)

    # Additional script execution goes here, within the virtual environment context
    # For example:
    from src.System.DataCollector import DataCollector
    from src.System.Service import Service

    # Load configuration variables
    config_file = os.path.join(script_dir, 'settings.conf')
    config = read_config(config_file)

    sender_email = config["SENDER_MAIL"]
    mail_password = config["SENDER_PASSWORD"]
    receiver_email = config["RECEIVER_MAIL"]
    smtp_server_address = config["SMTP_SERVER_ADDRESS"]
    smtp_server_port = config["SMTP_SERVER_PORT"]
    disk_path = config["DISK_PATH"]

    pi_external = config["PI_EXTERNAL"]
    pi_external_port = config["PI_EXTERNAL_PORT"]
    pi_local_port = config["PI_LOCAL_PORT"]
    pi_user = config["PI_USER"]

    # System Variables
    data_collector = DataCollector()
    operating_system = data_collector.get_operating_system()

    # Check if the disk path should be chosen automatically
    if disk_path == "auto":
        if operating_system == "Windows":
            disk_path = "C:\\"
        else:
            disk_path = "/"

    service = Service(script_dir)

    # Example of email sending functionality
    mail_sender = MailSender(sender_email, mail_password, receiver_email, script_dir, disk_path, operating_system,
                             smtp_server_address, smtp_server_port, pi_external, pi_external_port, pi_local_port, pi_user)
    mail_sender.send_mail()
