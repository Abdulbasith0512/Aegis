import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.loader import settings

logger = logging.getLogger("aegisai.email")

class EmailService:
    """
    Enterprise Outbound Email Service handles team invitations, SLA alert notifications,
    and audit digests. Falls back to console printing in local environments.
    """

    def send_invite_email(self, email: str, role_name: str, invite_link: str) -> bool:
        """
        Dispatches an HTML invitation email containing a secure signup link.
        """
        subject = f"Invitation to join AegisAI OS as {role_name}"
        html_content = f"""
        <html>
          <body style="font-family: sans-serif; background-color: #0d0f14; color: #e2e8f0; padding: 24px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #121620; padding: 32px; border-radius: 8px; border: 1px solid #1c1c24;">
              <h2 style="color: #ffffff; border-bottom: 1px solid #1c1c24; padding-bottom: 12px;">AegisAI OS Invitation</h2>
              <p>You have been invited to join the AegisAI Operations team as a <strong>{role_name}</strong>.</p>
              <p style="margin: 24px 0;">
                <a href="{invite_link}" style="background: linear-gradient(135deg, #6366f1, #00d4ff); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                  Complete Setup & Register
                </a>
              </p>
              <p style="font-size: 11px; color: #52525e;">If the button doesn't work, copy and paste this link into your browser:<br/>{invite_link}</p>
            </div>
          </body>
         </html>
        """

        # Verify SMTP configurations
        use_smtp = bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)

        if not use_smtp:
            # ── Fallback Console Log Simulator ──
            box_width = 80
            print("\n" + "=" * box_width)
            print(" [EMAIL DISPATCH SIMULATOR] (No SMTP credentials configured in .env)".center(box_width))
            print("=" * box_width)
            print(f" To:       {email}")
            print(f" Subject:  {subject}")
            print(f" Role:     {role_name}")
            print(f" URL Link: {invite_link}")
            print("-" * box_width)
            print(" HTML Body Preview:")
            print(f"   You have been invited to join AegisAI OS as a {role_name}.")
            print(f"   Invite Link: {invite_link}")
            print("=" * box_width + "\n")
            
            logger.info(f"[EMAIL SIMULATION] Outbound invitation email logged to console for: {email}")
            return True

        # Send SMTP mail
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = email

            msg.attach(MIMEText(html_content, "html"))

            # Connect SMTP TLS
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM, email, msg.as_string())
                
            logger.info(f"Outbound invitation email successfully dispatched to: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch outbound invitation email to {email}: {e}")
            return False

# Global email service instance
email_service = EmailService()
