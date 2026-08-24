"""
Sends observation-notification emails via Gmail SMTP.
Set EMAIL_ADDRESS and EMAIL_APP_PASSWORD (or MAIL_USERNAME / MAIL_PASSWORD) in Render environment.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Port 465 (SSL) Render par port 587 se ziada reliable aur fast hai
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def send_observation_email(observation: dict, department: str, manager: str, manager_email: str) -> bool:
    """observation is a dict like Observation.to_dict(). Returns True if sent."""
    
    # Fallback support agar Render par MAIL_USERNAME/MAIL_PASSWORD ke naam se variables hon
    sender = os.environ.get("EMAIL_ADDRESS") or os.environ.get("MAIL_USERNAME")
    app_password = os.environ.get("EMAIL_APP_PASSWORD") or os.environ.get("MAIL_PASSWORD")

    if not sender or not app_password or not manager_email:
        print("--- EMAIL SKIPPED: Missing sender, app_password, or manager_email ---")
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
          <tr><td style="padding: 8px 0; color: #666;">Time</td><td style="padding: 8px 0;">{observation.get('created_at', 'N/A')}</td></tr>
        </table>
        <p style="background: #f5f5f5; padding: 14px; border-radius: 6px; border-left: 3px solid #ff9f43;">
          {observation.get('english_translation', 'No description available')}
        </p>
        <p style="margin-top: 24px;">Please review and action this in the Bolo Safety dashboard at your earliest convenience.</p>
        <p style="color: #999; font-size: 12px; margin-top: 32px;">This is an automated notification from Bolo Safety. Please do not reply to this email.</p>
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Bolo Safety <{sender}>"
    msg["To"] = manager_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        # SMTP_SSL aur timeout=10 Worker Timeout issue fix karta hai
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.login(sender, app_password)
            server.sendmail(sender, [manager_email], msg.as_string())
        print(f"--- EMAIL SENT SUCCESSFULLY TO {manager_email} ---")
        return True
    except Exception as e:
        print(f"--- EMAIL SEND FAILED: {e} ---")
        return False
