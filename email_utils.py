# email_utils.py
import csv
import os
import ssl
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from config import SENDER_EMAIL, APP_PASSWORD, SMTP_SERVER, SMTP_PORT


# ================= LOGGING SETUP =================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "activity_log.txt")


def log_activity(message):
    """
    Write a timestamped log entry to file and return it for GUI display.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(log_line + "\n")
    return log_line


# ================= TEMPLATE HANDLING =================
def load_template(template_file="email_template.txt"):
    """
    Load the email body template from a text file.
    """
    try:
        with open(template_file, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as error:
        log_activity(f"ERROR loading template '{template_file}': {error}")
        return None


# ================= CSV HANDLING =================
def read_csv_file(path):
    """
    Read CSV file and return list of dictionaries.
    Expected columns: name, email, subject
    """
    rows = []
    try:
        with open(path, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(row)
        log_activity(f"Recipient list loaded successfully from {path}")
    except Exception as error:
        log_activity(f"ERROR loading recipients from {path}: {error}")
    return rows


# ================= EMAIL SENDING =================
def send_message(
    recipient_email,
    subject,
    plain_text_body,
    html_body=None,
    attachment_path=None,
    max_retries=3
):
    """
    Send a single email message using SMTP with retry and exponential backoff.

    Returns:
        (bool success, str log_message)
    """

    # Defensive validation (industry best practice)
    if not recipient_email:
        return False, log_activity("ERROR: Empty recipient email address")

    if not SENDER_EMAIL or not APP_PASSWORD:
        return False, log_activity("ERROR: Sender credentials are missing")

    retry_delay = 2

    for attempt in range(1, max_retries + 1):
        try:
            # Build email
            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient_email
            msg["Subject"] = subject

            # Plain text body
            msg.attach(MIMEText(plain_text_body, "plain"))

            # Optional HTML body
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            # Optional attachment
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment_file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(attachment_path)}"'
                )
                msg.attach(part)

            # Secure SMTP connection
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as smtp:
                smtp.login(SENDER_EMAIL, APP_PASSWORD)
                smtp.send_message(msg)

            # Success
            return True, log_activity(f"Email sent to {recipient_email}")

        except Exception as error:
            log_activity(f"Attempt {attempt} failed for {recipient_email}: {error}")

            if attempt == max_retries:
                return False, log_activity(f"Final failure for {recipient_email}")

            time.sleep(retry_delay)
            retry_delay *= 2  # exponential backoff
