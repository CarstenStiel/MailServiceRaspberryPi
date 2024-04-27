"""
Deprecated

Not needed anymore

By: Timothy
"""
import sys
import time
import psutil
import requests
import platform
import socket
import os


class DataCollector:
    """
    A class for collecting system information.

    This class contains methods for retrieving the operating system,
    system information including uptime, disk usage, and CPU usage,
    and for obtaining the global IP address.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_local_ip():
        """
        Retrieves the local IP address of the device.

        Returns:
            str: The local IP address of the device, or None if an error occurs.
        """
        try:
            # Create a UDP socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Connect to a known external server (here, Google's public DNS server)
            # This step is necessary to determine the local IP address of the machine
            # The port number (80) is irrelevant for our purposes
            s.connect(("8.8.8.8", 80))

            # Get the local IP address of the connected socket
            # This is our local IP address
            local_ip = s.getsockname()[0]

            # Close the socket connection as it's no longer needed
            s.close()

            # Return the retrieved local IP address
            return local_ip
        except socket.error:
            # If there's an error retrieving the IP address, return None
            return None

    @staticmethod
    def get_operating_system():
        """
        Checks the operating system and returns a message along with the detected system type.

        Returns:
            str: The detected system type (Windows, Linux, Raspberry).
        """
        # Get the system type
        system = platform.system()

        # Check if the system is Windows
        if system == "Windows":
            print("You are on a Windows system.")
            return "Windows"
        # Check if the system is Linux
        elif system == "Linux":
            # Check if it's a Raspberry Pi
            if platform.machine() == "armv7l" or os.path.exists('/boot/config.txt'):
                print("You are on a Raspberry Pi.")
                return "Raspberry"
            else:
                print("You are on a Linux system.")
                return "Linux"
        else:
            print("The operating system is not recognized. Exiting...")
            sys.exit(1)

    @staticmethod
    def system_info(disk_path):
        """
        Collects information about the system.

        Args:
            disk_path (str): The path to the disk to collect information from.

        Returns:
            dict: A dictionary containing system information including
                  uptime, disk usage, and CPU usage.
        """
        # System uptime in seconds since the last boot
        uptime_seconds = time.time() - psutil.boot_time()

        # Convert seconds to days, hours, minutes, and seconds
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Disk information
        disk_usage = psutil.disk_usage(disk_path)
        total_disk_gb = disk_usage.total / (1024 ** 3)  # Total disk space in gigabytes
        used_disk_gb = disk_usage.used / (1024 ** 3)  # Used disk space in gigabytes
        free_disk_gb = disk_usage.free / (1024 ** 3)  # Free disk space in gigabytes

        # CPU usage
        cpu_percent_now = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_physical = psutil.cpu_count(logical=False)

        # RAM-Information
        ram = psutil.virtual_memory()
        total_ram_gb = ram.total / (1024 ** 3)
        used_ram_gb = ram.used / (1024 ** 3)
        available_ram_gb = ram.available / (1024 ** 3)
        ram_percent = ram.percent

        # Partitions
        disk_partitions = psutil.disk_partitions(all=True)

        return {
            "uptime_days": int(days),
            "uptime_hours": int(hours),
            "uptime_minutes": int(minutes),
            "uptime_seconds": int(seconds),
            "total_memory": total_disk_gb,
            "used_memory": used_disk_gb,
            "free_memory": free_disk_gb,
            "cpu_percent_now": cpu_percent_now,
            "cpu_freq": cpu_freq,
            "cpu_physical": cpu_physical,
            "total_ram_gb": total_ram_gb,
            "used_ram_gb": used_ram_gb,
            "available_ram_gb": available_ram_gb,
            "ram_percent": ram_percent,
            "disk_partitions": disk_partitions
        }

    @staticmethod
    def get_global_ip():
        """
        Retrieves the global IP address.

        Returns:
            str: The global IP address of the device.
                 None if the IP address retrieval fails.
        """
        try:
            # API endpoint for retrieving the global IP address
            url = 'https://api.ipify.org'

            # Send HTTP request to the API
            response = requests.get(url)

            # Check response and extract the global IP address
            if response.status_code == 200:
                return response.text
            else:
                print("Error retrieving global IP:", response.status_code)
                return None
        except Exception as e:
            print("Error:", e)
            return None
