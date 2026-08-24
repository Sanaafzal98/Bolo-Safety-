"""
Sends observation-notification emails via Gmail SMTP.
Uses port 587 + STARTTLS with a short timeout so a slow/blocked connection
can never hang the web server (which previously caused worker crashes).
Set EMAIL_ADDRESS and EMAIL_APP_PASSWORD in your Render environment.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_observation_email(observation: dict, department: str, manager: str, manager_email: str) -> bool:
    sender = os.environ.get("EMAIL_ADDRESS")
    app_password = os.environ.get("EMAIL_APP_PASSWORD")

    if not sender or not app_password:
        print("--- EMAIL SKIPPED: EMAIL_ADDRESS or EMAIL_APP_PASSWORD not set ---")
        return False
    if not manager_email:
        print("--- EMAIL SKIPPED: no manager_email ---")
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
          <tr><td style="padding: 8px 0; color: #666;">Severity</td><td style="padding: 8px 0; font-weight: bold;">{observation.get('severity', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #666;">Location</td><td style="padding: 8px 0; font-weight: bold;">{observation.get('location', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #666;">Reported by</td><td style="padding: 8px 0;">{observation.get('reporter_name', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #666;">Time</td><td style="padding: 8px 0;">{observation.get('created_at', 'N/A')}</td></tr>
        </table>
        <p style="background: #f5f5f5; padding: 14px; border-radius: 6px; border-left: 3px solid #ff9f43;">
          {observation.get('english_translation', '')}
        </p>
        <p style="color: #999; font-size: 12px; margin-top: 32px;">This is an automated notification from Bolo Safety.</p>
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Bolo Safety <{sender}>"
    msg["To"] = manager_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(sender, app_password)
            server.sendmail(sender, [manager_email], msg.as_string())
        print(f"--- EMAIL SENT to {manager_email} ---")
        return True
    except Exception as e:
        print(f"--- EMAIL FAILED: {e} ---")
        return False
