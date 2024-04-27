import os
import subprocess


class Service:
    def __init__(self, script_dir):
        # Initialize attributes for sudo password and script directory
        self.script_dir = script_dir

    def setLinuxService(self):
        # Construct the old and new ExecStart commands
        old_command = f"ExecStart=/path/to/venv/exec /path/to/setup.py"
        new_command = f"ExecStart={os.path.join(self.script_dir, '.venv', 'bin', 'python')} {os.path.join(self.script_dir, 'main.py')}"

        try:
            # Copy the service file to the system directory
            subprocess.run(["cp", os.path.join(self.script_dir, 'info-mail.service'), "/etc/systemd/system"],
                           check=True, shell=False)
            print("Service file was successfully copied to the system directory.")

            # Open the copied service file in read mode
            with open("/etc/systemd/system/info-mail.service", 'r') as file:
                # Read all lines from the file
                lines = file.readlines()

            # Iterate through the lines and replace the old command with the new one
            for i, line in enumerate(lines):
                if old_command in line:
                    lines[i] = line.replace(old_command, new_command)

            # Write the modified lines back to the file
            with open("/etc/systemd/system/info-mail.service", 'w') as file:
                file.writelines(lines)

            print("Replacement completed successfully.")
        except FileNotFoundError:
            print("File not found.")
        except subprocess.CalledProcessError as e:
            print("Error copying service file to the system directory:", e)
        except Exception as e:
            print("An error occurred:", e)

        # Restart the service
        try:
            subprocess.run(["systemctl", "restart", "info-mail.service"], shell=False)
            print("Service was successfully restarted.")
        except subprocess.CalledProcessError as e:
            print("Service could not be restarted: ", e)

    @staticmethod
    def check_file_exists(directory, filename):
        """
        Checks if a file exists in the specified directory.

        Args:
            directory (str): The directory to check for the file.
            filename (str): The name of the file to check for.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        # Full path to the file
        file_path = os.path.join(directory, filename)

        # Check if the file exists
        if os.path.exists(file_path):
            print(f"The file '{filename}' exists in the directory '{directory}'.")
            return True
        else:
            print(f"The file '{filename}' does not exist in the directory '{directory}'.")
            return False
