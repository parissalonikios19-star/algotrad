import os
import smtplib
from email.message import EmailMessage
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def send_alert(message_body):
    load_dotenv()
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_user or not email_pass:
        logger.warning("[!] Email credentials missing. Skipping email alert.")
        return
    
    # email from myself to myself
    msg = EmailMessage()
    msg.set_content(message_body)
    msg['Subject'] = '!! ALGO TRADING ALERT !!'
    msg['From'] = email_user
    msg['To'] = email_user

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_user, email_pass)
            smtp.send_message(msg)
        logger.info("[*] Email alert sent successfully!")
    except Exception as e:
        logger.error(f"[!] Failed to send email alert: {e}")