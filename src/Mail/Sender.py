import os
import psutil
import smtplib
import ssl
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid

from ..System.DataCollector import DataCollector
from .HTMLBuilder import HTMLBuilder


class MailSender:
    def __init__(self, sender_email, mail_password, receiver_email, script_dir, disk_path, operating_system, smtp_server_address, smtp_server_port, pi_external, pi_external_port, pi_local_port,
                 pi_user):
        """
        Initialize the MailSender object.

        Args:
            sender_email (str): Sender's email address.
            mail_password (str): Password of the sender's email account.
            receiver_email (str): Receiver's email address.
            script_dir (str): Directory path of the script.
            disk_path (str): Path of the disk.
            operating_system (str): Operating system type.
            smtp_server_address (str): SMTP server address.
            smtp_server_port (int): SMTP server port.
        """
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.mail_password = mail_password
        self.script_dir = script_dir
        self.disk_path = disk_path
        self.operating_system = operating_system
        self.smtp_server_address = smtp_server_address
        self.smtp_server_port = smtp_server_port
        self.pi_external = pi_external
        self.pi_external_port = pi_external_port
        self.pi_local_port = pi_local_port
        self.pi_user = pi_user

        self.dataCollector = DataCollector()
        self.html_builder = HTMLBuilder()
        self.local_ip = self.dataCollector.get_local_ip()
        self.global_ip = self.dataCollector.get_global_ip()

    def pi_mail(self, info):
        """
        Send an email with system information for Raspberry Pi.

        Args:
            info (dict): System information.

        Returns:
            MIMEMultipart: Message object.
        """

        # Add styles to the HTMLBuilder
        self.html_builder.add_style("""
            .highlight {
                width: fit-content;
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            img {
                height: 40px;
                margin-right: 10px;
                vertical-align: middle;
            }
        """)

        external_ip = (
                f"<p>Your external IP is: {self.global_ip}</p>" +
                "<p>To connect to your Raspberry Pi, use:</p>" +
                f"<pre class ='highlight'> ssh -p {self.pi_external_port} {self.pi_user}@{self.global_ip} </pre>"
        )

        local_ip = (
                f"<p>Your local IP is: {self.local_ip}</p>" +
                "<p>To connect to your Raspberry Pi, use:</p>" +
                f"<pre class ='highlight'> ssh -p {self.pi_local_port} {self.pi_user}@{self.local_ip} </pre>"
        )

        network = external_ip + local_ip if self.pi_external == True else local_ip

        # Add body content to the HTMLBuilder
        self.html_builder.add_body_content(f"""
            <div class="main">
                <div>
                    <img src="cid:image_cid" alt="Raspberry Pi Logo">
                </div>
                <div style="height: 20px;"></div>
                <div>
                    <h2>Here are the current details of your Raspberry Pi:</h2>
                    <div style="height: 20px;"></div>
                    <div class="device-info">
                        <h3>Device Information:</h3>
                        <p>Name: {socket.gethostname()}</p>
                        <p>System uptime: {info["uptime_days"]}d, {info["uptime_hours"]}h, {info["uptime_minutes"]}min</p>
                        <br>
                        <div>
                            <h3>Network:</h3>
                            {network}
                        </div>
                        <br>
                        <h4>Storage</h4>
                        <p>Total Storage: {round(info["total_memory"], 2)} GB</p>
                        <p>Used Storage: {round(info["used_memory"], 2)} GB; Free Storage: {round(info["free_memory"], 2)} GB</p>
                        <br>
                        <h4>RAM</h4>
                        <p>Total RAM: {round(info["total_ram_gb"], 2)} GB; Usage: {round(info["ram_percent"], 2)}%</p>
                        <p>Used RAM: {round(info["used_ram_gb"], 2)} GB; Free RAM: {round(info["available_ram_gb"], 2)}</p>
                    </div>
                </div>
            </div>
        """)

        # Get the HTML content from the HTMLBuilder
        html_content = self.html_builder.get_html()

        # Create MIMEText object for the HTML message
        message = MIMEMultipart()
        message.attach(MIMEText(html_content, "html"))

        # Generate image content ID
        image_cid = make_msgid(domain=os.path.join(self.script_dir, 'assets/raspberry_pi_logo.png'))

        # Add image to the attachment
        with open(os.path.join(self.script_dir, 'assets/raspberry_pi_logo.png'), 'rb') as file:
            image = MIMEImage(file.read())
        image.add_header('Content-ID', '<image_cid>')
        message.attach(image)

        # Define sender, receiver, and subject
        message["Subject"] = "Daily information from your Raspberry Pi"
        message["From"] = "Raspberry Pi <" + self.sender_email + ">"
        message["To"] = self.receiver_email

        return message

    def windows_mail(self, info):
        """
        Send an email with system information for Windows systems.

        Args:
            info (dict): System information.

        Returns:
            MIMEMultipart: Message object.
        """
        # Add styles to the HTMLBuilder
        self.html_builder.add_style("""
            img {
                height: 35px;
                margin-right: 10px;
                vertical-align: middle;
            }
        """)

        # Collect information about drives
        drives = ""
        for disk_partition in info["disk_partitions"]:
            if "fixed" in disk_partition.opts:
                disk_partition_path = disk_partition.mountpoint + "\\"
                disk_usage = psutil.disk_usage(disk_partition_path)
                total_gb = disk_usage.total / (1024 ** 3)
                used_gb = disk_usage.used / (1024 ** 3)
                free_gb = disk_usage.free / (1024 ** 3)
                drive_path = ':\\'
                drives += (
                    f"<p>Partition {disk_partition.device.replace(drive_path, ' ')} total: {round(total_gb, 2)} GB</p>"
                    f"<p>Used: {round(used_gb, 2)} GB; Free: {round(free_gb, 2)} GB</p>"
                )

        # Create HTML content
        html_content = f"""
            <div class="main">
                <div>
                    <img src="cid:image_cid" alt="Windows Logo">
                </div>
                <div style="height: 20px;"></div>
                <div>
                    <h2>Here are the current details:</h2>
                    <div style="height: 20px;"></div>
                    <div class="device-info">
                        <h3>Device Information:</h3>
                        <p>Name: {socket.gethostname()}</p>
                        <p>System uptime: {info["uptime_days"]}d, {info["uptime_hours"]}h, {info["uptime_minutes"]}min</p>
                        <br>
                        <h4> Storage</h4>
                        {drives}
                        <br>
                        <h4> RAM</h4>
                        <p>Total: {round(info["total_ram_gb"], 2)} GB; Usage: {round(info["ram_percent"], 2)}%</p>
                        <p>Used: {round(info["used_ram_gb"], 2)} GB; Free: {round(info["available_ram_gb"], 2)} GB</p>
                        <br>
                        <h4> CPU</h4>
                        <p>Physical CPUs: {info["cpu_physical"]}</p>
                        <p>Current usage: {info["cpu_percent_now"]}%</p>
                        <br>
                        <div>
                            <h3>Network:</h3>
                            <p>Local IP: {self.local_ip}</p>
                            <p>Global IP: {self.global_ip}</p>                            
                        </div>
                    </div>
                </div>
            </div>
        """

        # Create a MIME object for the HTML message
        message = MIMEMultipart()
        message.attach(MIMEText(html_content, "html"))

        # Add an image as an attachment
        image_cid = make_msgid(domain=os.path.join(self.script_dir, 'assets/windows_logo.png'))
        with open(os.path.join(self.script_dir, 'assets/windows_logo.png'), 'rb') as file:
            image = MIMEImage(file.read())
        image.add_header('Content-ID', '<image_cid>')
        message.attach(image)

        # Define sender, receiver, and subject
        message["Subject"] = "Daily information from your Windows System"
        message["From"] = f"Windows System <{self.sender_email}>"
        message["To"] = self.receiver_email

        return message

    def linux_mail(self, info):
        """
        Send an email with system information from your Linux System.

        Args:
            info (dict): System information.

        Returns:
            MIMEMultipart: Message object.
        """

        # Add styles to the HTMLBuilder
        self.html_builder.add_style("""
            img {
                height: 100px;
                margin-right: 10px;
                vertical-align: middle;
            }
        """)

        # Add body content to the HTMLBuilder
        self.html_builder.add_body_content(f"""
            <div class="main">
                <div>
                    <img src="cid:image_cid" alt="Linux Logo">
                </div>
                <div style="height: 20px;"></div>
                <div>
                    <h2>Here are the current details:</h2>
                    <div style="height: 20px;"></div>
                    <div class="device-info">
                        <h3>Device Information:</h3>
                        <p>Name: {socket.gethostname()}</p>
                        <p>System uptime: {info["uptime_days"]}d, {info["uptime_hours"]}h, {info["uptime_minutes"]}min</p>
                        <br>
                        <h4> Storage</h4>
                        <p>Total Storage: {round(info["total_memory"], 2)} GB</p>
                        <p>Used Storage: {round(info["used_memory"], 2)} GB; Free Storage: {round(info["free_memory"], 2)} GB</p>
                        <br>
                        <h4> RAM</h4>
                        <p>Total RAM: {round(info["total_ram_gb"], 2)} GB; Usage: {round(info["ram_percent"], 2)}%</p>
                        <p>Used RAM: {round(info["used_ram_gb"], 2)} GB; Free RAM: {round(info["available_ram_gb"], 2)}</p>
                        <br>
                        <h4> CPU</h4>
                        <p>Physical CPUs: {info["cpu_physical"]}</p>
                        <p>Current usage: {info["cpu_percent_now"]}%</p>
                        <br>
                        <div>
                            <h3>Network:</h3>
                            <p>Local IP: {self.local_ip}</p>
                            <p>Global IP: {self.global_ip}</p>                            
                        </div>
                    </div>
                </div>
            </div>
        """)

        # Get the HTML content from the HTMLBuilder
        html_content = self.html_builder.get_html()

        # Create MIMEText object for the HTML message
        message = MIMEMultipart()
        message.attach(MIMEText(html_content, "html"))

        # Generate image content ID
        image_cid = make_msgid(domain=os.path.join(self.script_dir, 'assets/linux_logo.png'))

        # Add image to the attachment
        with open(os.path.join(self.script_dir, 'assets/linux_logo.png'), 'rb') as file:
            image = MIMEImage(file.read())
        image.add_header('Content-ID', '<image_cid>')
        message.attach(image)

        # Define sender, receiver, and subject
        message["Subject"] = "Daily information from your Linux System"
        message["From"] = "Linux System <" + self.sender_email + ">"
        message["To"] = self.receiver_email

        return message

    def send_mail(self):
        """
        Send an email with system information based on the operating system.
        """
        # Additional variables
        info = self.dataCollector.system_info(self.disk_path)

        # Default Mail styles
        self.html_builder.add_style("""
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .main {
                width: 100hv;
                height: 100hv;
                margin: auto;
                padding: 20px;
                background-color: #fff;
            }
            h2, h3, h4, p {
                margin: 0.5rem;
            }
            img {
                height: 40px;
                margin-right: 10px;
                vertical-align: middle;
            }
        """)

        # Determine the operating system and construct the message accordingly
        if self.operating_system == "Windows":
            message = self.windows_mail(info)
        elif self.operating_system == "Raspberry":
            message = self.pi_mail(info)
        else:
            message = self.linux_mail(info)

        # Establish a secure connection with the server and send the email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server_address, self.smtp_server_port, context=context) as server:
            server.login(self.sender_email, self.mail_password)
            server.sendmail(self.sender_email, self.receiver_email, message.as_string())
        print("Mail send.")
