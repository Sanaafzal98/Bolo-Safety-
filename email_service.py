"""
Sends observation-notification emails via the Resend HTTPS API
(https://resend.com). Render blocks outbound SMTP (port 587/465), which is
why the old Gmail-SMTP version failed with "[Errno 101] Network is
unreachable". Resend's API runs over plain HTTPS (port 443), which Render
always allows outbound.

Set RESEND_API_KEY in your Render environment.

NOTE (testing phase): until a custom domain is verified on Resend, the
"onboarding@resend.dev" sender can only deliver to the email address the
Resend account itself was created with (bolosafety@gmail.com). Sending to
any other address will fail with a 403 until the domain is verified.
"""

import os
import requests

RESEND_API_URL = "https://api.resend.com/emails"


def send_observation_email(observation: dict, department: str, manager: str, manager_email: str) -> bool:
    api_key = os.environ.get("RESEND_API_KEY")

    if not api_key:
        print("--- EMAIL SKIPPED: RESEND_API_KEY not set ---")
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

    payload = {
        "from": "Bolo Safety <onboarding@resend.dev>",
        "to": [manager_email],
        "subject": subject,
        "html": html_body,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        print(f"--- ATTEMPTING EMAIL TO: {manager_email} FOR LOCATION: {observation.get('location')} ---")
        resp = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
        if resp.status_code in (200, 201, 202):
            print(f"--- EMAIL SENT to {manager_email} (id: {resp.json().get('id')}) ---")
            return True
        print(f"--- EMAIL FAILED: {resp.status_code} {resp.text} ---")
        return False
    except Exception as e:
        print(f"--- EMAIL FAILED: {e} ---")
        return False
