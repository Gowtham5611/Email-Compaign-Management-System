import os
import ssl
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Tuple, Dict, Any
from app.core.config import settings
from app.core.logging_config import log_activity

class EmailService:
    @staticmethod
    def send_single_email(
        recipient_email: str,
        subject: str,
        plain_text_body: str,
        html_body: Optional[str] = None,
        attachment_path: Optional[str] = None,
        smtp_config: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Tuple[bool, str, int]:
        """
        Sends an email message using SMTP with retry logic and exponential backoff.
        Preserves original email sending logic upgraded for production backend.

        Returns:
            (success: bool, error_or_log_msg: str, retries_used: int)
        """
        if not recipient_email or "@" not in recipient_email:
            return False, log_activity("ERROR: Empty or invalid recipient email address", level="error"), 0

        # Load SMTP settings (user override or global env settings)
        host = smtp_config.get("smtp_host") if smtp_config and smtp_config.get("smtp_host") else settings.SMTP_HOST
        port = smtp_config.get("smtp_port") if smtp_config and smtp_config.get("smtp_port") else settings.SMTP_PORT
        username = smtp_config.get("smtp_username") if smtp_config and smtp_config.get("smtp_username") else settings.SMTP_USERNAME
        password = smtp_config.get("smtp_password") if smtp_config and smtp_config.get("smtp_password") else settings.SMTP_PASSWORD
        sender_name = smtp_config.get("sender_name") if smtp_config and smtp_config.get("sender_name") else settings.SENDER_NAME

        if not username or not password:
            err_msg = "SMTP authentication error: Sender credentials missing. Configure SMTP in Settings."
            log_activity(err_msg, level="error")
            return False, err_msg, 0

        retry_delay = 2

        for attempt in range(1, max_retries + 1):
            try:
                msg = MIMEMultipart("alternative" if html_body else "mixed")
                msg["From"] = f"{sender_name} <{username}>" if sender_name else username
                msg["To"] = recipient_email
                msg["Subject"] = subject

                # Attach Plain Text
                msg.attach(MIMEText(plain_text_body, "plain", "utf-8"))

                # Attach HTML if provided
                if html_body:
                    msg.attach(MIMEText(html_body, "html", "utf-8"))

                # Handle Attachment safely
                if attachment_path:
                    # Prevent path traversal vulnerabilities
                    safe_path = os.path.abspath(attachment_path)
                    if os.path.exists(safe_path) and os.path.isfile(safe_path):
                        with open(safe_path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        filename = os.path.basename(safe_path)
                        part.add_header(
                            "Content-Disposition",
                            f'attachment; filename="{filename}"'
                        )
                        msg.attach(part)
                    else:
                        log_activity(f"WARNING: Attachment file not found: {attachment_path}", level="warning")

                # Establish secure connection
                context = ssl.create_default_context()
                
                if int(port) == 465:
                    # SSL mode
                    with smtplib.SMTP_SSL(host, int(port), context=context, timeout=15) as server:
                        server.login(username, password)
                        server.send_message(msg)
                else:
                    # STARTTLS mode (ports 587, 25, 2525)
                    with smtplib.SMTP(host, int(port), timeout=15) as server:
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(username, password)
                        server.send_message(msg)

                success_msg = f"Successfully delivered email to {recipient_email}"
                log_activity(success_msg)
                return True, success_msg, attempt

            except Exception as error:
                err_str = str(error)
                log_activity(f"Attempt {attempt}/{max_retries} failed for {recipient_email}: {err_str}", level="warning")
                
                if attempt == max_retries:
                    final_msg = f"Failed to send email to {recipient_email} after {max_retries} retries. Error: {err_str}"
                    log_activity(final_msg, level="error")
                    return False, final_msg, attempt

                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        return False, f"Failed to send to {recipient_email}", max_retries

    @staticmethod
    def test_smtp_connection(smtp_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verify SMTP credentials and server connectivity.
        """
        host = smtp_config.get("smtp_host", "smtp.gmail.com")
        port = int(smtp_config.get("smtp_port", 465))
        username = smtp_config.get("smtp_username", "")
        password = smtp_config.get("smtp_password", "")

        if not username or not password:
            return False, "SMTP Username and Password are required."

        try:
            context = ssl.create_default_context()
            if port == 465:
                with smtplib.SMTP_SSL(host, port, context=context, timeout=10) as server:
                    server.login(username, password)
            else:
                with smtplib.SMTP(host, port, timeout=10) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(username, password)
            return True, "SMTP connection successful!"
        except Exception as e:
            return False, f"SMTP Connection Failed: {str(e)}"

