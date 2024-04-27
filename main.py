"""
Main script to maintain service functionality and send emails at specified time.
"""

import time
import threading
import os

from src.Mail.Sender import MailSender
from src.System.DataCollector import DataCollector


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


def schedule_task():
    """
    Schedules the task to send the email at the specified time.
    """
    while True:
        current_time = time.localtime()
        print(current_time)  # Debugging output
        if current_time.tm_hour == config["SEND_HOUR"] and current_time.tm_min == config["SEND_MINUTE"]:
            mail_sender = MailSender(sender_email, mail_password, receiver_email, script_dir, disk_path, operating_system,
                                     smtp_server_address, smtp_server_port, pi_external, pi_external_port, pi_local_port, pi_user)
            mail_sender.send_mail()
            print("Mail has been sent")  # Debugging output
            print(f"Time: {current_time}")  # Debugging output
        time.sleep(60)  # Check every minute if it's time to send the email


if __name__ == "__main__":
    # Get the directory path where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Set the path to the configuration file relative to the script directory
    config_file = os.path.join(script_dir, 'settings.conf')

    # Load configurations from the file
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

    # Initialize system variables
    data_collector = DataCollector()
    operating_system = data_collector.get_operating_system()

    # Check if the disk path should be chosen automatically
    if disk_path == "auto":
        if operating_system == "Windows":
            disk_path = "C:\\"
        else:
            disk_path = "/"

    # Start the scheduled task in a background thread
    threading.Thread(target=schedule_task, daemon=True).start()

    # Infinite loop to keep the script running
    while True:
        time.sleep(1)  # Debugging output to keep the script running
