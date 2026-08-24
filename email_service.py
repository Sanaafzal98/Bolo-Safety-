"""
Sends notification emails directly via Gmail SMTP.
Uses Port 587 with STARTTLS and timeout to prevent Render worker timeouts.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_observation_email(observation: dict, department: str, manager: str, manager_email: str) -> bool:
    sender_email = os.environ.get("SMTP_EMAIL")
    sender_password = os.environ.get("SMTP_PASSWORD")

    if not sender_email or not sender_password:
        print("--- EMAIL SKIPPED: Missing SMTP_EMAIL or SMTP_PASSWORD in env ---")
        return False

    if not manager_email:
        print("--- EMAIL SKIPPED: Missing manager_email ---")
        return False

    subject = f"[Bolo Safety] New {observation.get('severity', 'Normal')} severity report — {observation.get('location') or 'Not specified'}"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
      <div style="background: #1a2634; padding: 20px; border-radius: 8px 8px 0 0;">
        <h2 style="color: #ff9f43; margin: 0;">⛑ Bolo Safety</h2>
        <p style="color: #c9d1d9; margin: 4px 0 0;">New safety observation for {department}</p>
      </div>
      <div style="border: 1px solid #e0e0e0; border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">
        <p>Hi {manager},</p>
        <p>A new safety observation has been logged that falls under your area. Details below:</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
          <tr><td style="padding: 8px 0; color: #666; width: 140px;">Category</td><td style="padding: 8px 0; font-weight: bold;">{observation.get('category', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #666;">Severity</td><td style="padding: 8px 0; font-weight: bold; color: {'#e03131' if observation.get('severity')=='High' else '#f08c00' if observation.get('severity')=='Medium' else '#2f9e44'};">{observation.get('severity', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #666;">Location</td><td style="padding: 8px 0; font-weight: bold;">{observation.get('location', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #666;">Reported by</td><td style="padding: 8px 0;">{observation.get('reporter_name', 'N/A')}</td></tr>
        </table>
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Bolo Safety <{sender_email}>"
    msg["To"] = manager_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        # Port 587 with STARTTLS & 10s timeout prevents worker hanging
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, manager_email, msg.as_string())
        print(f"--- EMAIL SENT SUCCESSFULLY TO {manager_email} VIA GMAIL ---")
        return True
    except Exception as e:
        print(f"--- EMAIL FAILED VIA GMAIL: {e} ---")
        return False
