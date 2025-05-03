# app/core/email.py
import logging
from typing import Optional
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Send an email using SMTP
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_SENDER
        message["To"] = to_email
        
        # Add text/plain part
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)
        
        # Add text/html part
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            server.sendmail(settings.SMTP_SENDER, to_email, message.as_string())
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_password_reset_email(email: str, reset_link: str) -> bool:
    """
    Send password reset email with link
    """
    subject = "Password Reset Request - Devflow"
    
    # HTML Content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #eeeeee;
            }}
            .header {{
                background-color: #4285F4;
                color: #ffffff;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .button {{
                display: inline-block;
                background-color: #4285F4;
                color: #ffffff;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #999999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Devflow Password Reset</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a request to reset your password for your Devflow account. If you didn't make this request, you can safely ignore this email.</p>
                <p>To reset your password, click the button below:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Your Password</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{reset_link}</p>
                <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours for security reasons.</p>
                <p>If you need any assistance, please contact our support team.</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
                <p>&copy; {datetime.datetime.now().year} Devflow. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Devflow Password Reset
    
    Hello,
    
    We received a request to reset your password for your Devflow account. If you didn't make this request, you can safely ignore this email.
    
    To reset your password, please visit the following link:
    
    {reset_link}
    
    This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours for security reasons.
    
    If you need any assistance, please contact our support team.
    
    This is an automated message, please do not reply to this email.
    
    © {datetime.datetime.now().year} Devflow. All rights reserved.
    """
    
    return send_email(email, subject, html_content, text_content)


def send_account_verification_email(email: str, verification_link: str) -> bool:
    """
    Send account verification email with link
    """
    subject = "Verify Your Account - Devflow"
    
    # HTML Content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #eeeeee;
            }}
            .header {{
                background-color: #4285F4;
                color: #ffffff;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .button {{
                display: inline-block;
                background-color: #4285F4;
                color: #ffffff;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #999999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Devflow</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Thank you for registering an account with Devflow. To complete your registration, please verify your email address.</p>
                <p>Click the button below to verify your account:</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Your Account</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{verification_link}</p>
                <p>If you did not create an account with us, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
                <p>&copy; {datetime.datetime.now().year} Devflow. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Welcome to Devflow
    
    Hello,
    
    Thank you for registering an account with Devflow. To complete your registration, please verify your email address.
    
    Please visit the following link to verify your account:
    
    {verification_link}
    
    If you did not create an account with us, you can safely ignore this email.
    
    This is an automated message, please do not reply to this email.
    
    © {datetime.datetime.now().year} Devflow. All rights reserved.
    """
    
    return send_email(email, subject, html_content, text_content)


def send_welcome_email(email: str, user_name: str = "") -> bool:
    """
    Send welcome email after account verification
    """
    subject = "Welcome to Devflow"
    
    greeting = f"Hello {user_name}," if user_name else "Hello,"
    
    # HTML Content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #eeeeee;
            }}
            .header {{
                background-color: #4285F4;
                color: #ffffff;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .button {{
                display: inline-block;
                background-color: #4285F4;
                color: #ffffff;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .features {{
                margin: 20px 0;
            }}
            .feature {{
                margin-bottom: 15px;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #999999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Devflow</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                <p>Your account has been successfully created and is now active. Thank you for joining Devflow!</p>
                <p>With your new account, you can:</p>
                <div class="features">
                    <div class="feature">
                        <strong>✅ Access powerful developer tools</strong>
                        <p>Streamline your workflow with our suite of integrated tools.</p>
                    </div>
                    <div class="feature">
                        <strong>✅ Connect with other developers</strong>
                        <p>Join a thriving community of like-minded professionals.</p>
                    </div>
                    <div class="feature">
                        <strong>✅ Track your projects</strong>
                        <p>Manage and monitor your development projects with ease.</p>
                    </div>
                </div>
                <p style="text-align: center;">
                    <a href="{settings.FRONTEND_URL}/dashboard" class="button">Go to Your Dashboard</a>
                </p>
                <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                <p>Best regards,<br>The Devflow Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
                <p>&copy; {datetime.datetime.now().year} Devflow. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Welcome to Devflow
    
    {greeting}
    
    Your account has been successfully created and is now active. Thank you for joining Devflow!
    
    With your new account, you can:
    
    ✅ Access powerful developer tools
    Streamline your workflow with our suite of integrated tools.
    
    ✅ Connect with other developers
    Join a thriving community of like-minded professionals.
    
    ✅ Track your projects
    Manage and monitor your development projects with ease.
    
    Visit your dashboard: {settings.FRONTEND_URL}/dashboard
    
    If you have any questions or need assistance, please don't hesitate to contact our support team.
    
    Best regards,
    The Devflow Team
    
    This is an automated message, please do not reply to this email.
    
    © {datetime.datetime.now().year} Devflow. All rights reserved.
    """
    
    return send_email(email, subject, html_content, text_content)


def send_notification_email(email: str, subject: str, message: str) -> bool:
    """
    Send a general notification email
    """
    # HTML Content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #eeeeee;
            }}
            .header {{
                background-color: #4285F4;
                color: #ffffff;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #999999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Devflow Notification</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>{message}</p>
                <p>If you have any questions, please contact our support team.</p>
                <p>Best regards,<br>The Devflow Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
                <p>&copy; {datetime.datetime.now().year} Devflow. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Devflow Notification
    
    Hello,
    
    {message}
    
    If you have any questions, please contact our support team.
    
    Best regards,
    The Devflow Team
    
    This is an automated message, please do not reply to this email.
    
    © {datetime.datetime.now().year} Devflow. All rights reserved.
    """
    
    return send_email(email, subject, html_content, text_content)