# utils/email_utils.py

from flask_mail import Message
from flask import current_app, render_template_string
from extensions import mail

def send_email(to, subject, body, attachments=None):
    try:
        msg = Message(subject, recipients=[to], body=body)

        # Attach files if any
        if attachments:
            for filename, data, content_type in attachments:
                msg.attach(filename, content_type, data)

        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False


def send_welcome_email(employee_email, employee_name, username, password, company_name="Construction Management"):
    """
    Send welcome email to new employee with credentials and instructions
    """
    try:
        # Email template with welcome content
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 20px;
                }
                .email-container {
                    max-width: 600px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    margin: 0 auto;
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                }
                .header h1 {
                    margin: 0;
                    font-size: 28px;
                }
                .content {
                    padding: 40px;
                }
                .welcome-section {
                    margin-bottom: 30px;
                }
                .welcome-section h2 {
                    color: #333;
                    font-size: 22px;
                    margin-top: 0;
                }
                .welcome-section p {
                    color: #666;
                    line-height: 1.6;
                    margin: 15px 0;
                }
                .credentials-section {
                    background-color: #f9f9f9;
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 4px;
                }
                .credentials-section h3 {
                    color: #333;
                    margin-top: 0;
                    font-size: 16px;
                }
                .credential-item {
                    margin: 12px 0;
                    padding: 10px;
                    background-color: #ffffff;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                }
                .credential-label {
                    color: #666;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }
                .credential-value {
                    color: #333;
                    font-size: 16px;
                    font-weight: bold;
                }
                .instructions-section {
                    background-color: #e8f4f8;
                    border-left: 4px solid #0288d1;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 4px;
                }
                .instructions-section h3 {
                    color: #0288d1;
                    margin-top: 0;
                    font-size: 16px;
                }
                .instructions-section ol {
                    color: #666;
                    line-height: 1.8;
                }
                .instructions-section li {
                    margin: 10px 0;
                }
                .important-notice {
                    background-color: #fff3e0;
                    border-left: 4px solid #ff9800;
                    padding: 15px;
                    margin: 25px 0;
                    border-radius: 4px;
                    color: #666;
                }
                .important-notice strong {
                    color: #ff9800;
                }
                .footer {
                    background-color: #f5f5f5;
                    padding: 20px;
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    border-top: 1px solid #e0e0e0;
                }
                .button {
                    display: inline-block;
                    background-color: #667eea;
                    color: white;
                    padding: 12px 30px;
                    border-radius: 4px;
                    text-decoration: none;
                    margin: 20px 0;
                    font-weight: 600;
                }
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🎉 Welcome to {{ company_name }}!</h1>
                </div>

                <div class="content">
                    <div class="welcome-section">
                        <h2>Hello {{ employee_name }},</h2>
                        <p>We're excited to have you join our team at <strong>{{ company_name }}</strong>! Your employee account has been created and is ready to use.</p>
                        <p>Below you'll find your login credentials and important instructions to get started.</p>
                    </div>

                    <div class="credentials-section">
                        <h3>📋 Your Login Credentials</h3>
                        <div class="credential-item">
                            <div class="credential-label">Username</div>
                            <div class="credential-value">{{ username }}</div>
                        </div>
                        <div class="credential-item">
                            <div class="credential-label">Password</div>
                            <div class="credential-value">{{ password }}</div>
                        </div>
                    </div>

                    <div class="instructions-section">
                        <h3>🚀 Getting Started - First Login Steps:</h3>
                        <ol>
                            <li><strong>Download the App:</strong> Download our mobile app from the App Store or Google Play Store</li>
                            <li><strong>Enter Your Credentials:</strong> Use the username and password above to log in</li>
                            <li><strong>Change Your Password:</strong> On your first login, you'll be required to change your password. Please create a strong, unique password that you'll remember</li>
                            <li><strong>Complete Your Profile:</strong> Update any additional profile information if needed</li>
                            <li><strong>Start Working:</strong> You're all set! Begin using the app to manage your tasks</li>
                        </ol>
                    </div>

                    <div class="important-notice">
                        <strong>⚠️ Important Security Notice:</strong>
                        <p>
                            • Keep your credentials confidential<br>
                            • Change your password immediately after your first login<br>
                            • Never share your password with anyone<br>
                            • If you forget your password, contact your administrator
                        </p>
                    </div>

                    <div class="welcome-section">
                        <h2>What You Can Do:</h2>
                        <p>With your account, you'll have access to:</p>
                        <ul>
                            <li>✅ Attendance tracking and punch in/out</li>
                            <li>✅ Expense submission and tracking</li>
                            <li>✅ Project assignments and details</li>
                            <li>✅ Vehicle and equipment access</li>
                            <li>✅ Task management and updates</li>
                        </ul>
                    </div>

                    <div class="welcome-section">
                        <h2>Need Help?</h2>
                        <p>If you have any questions or issues with your account, please contact your administrator or reach out to our support team.</p>
                    </div>
                </div>

                <div class="footer">
                    <p>© {{ company_name }} - All Rights Reserved</p>
                    <p>This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Render the template
        html_body = render_template_string(
            html_template,
            employee_name=employee_name,
            username=username,
            password=password,
            company_name=company_name
        )

        # Also create plain text version
        text_body = f"""
Welcome to {company_name}!

Hello {employee_name},

We're excited to have you join our team! Your employee account has been created.

YOUR LOGIN CREDENTIALS:
Username: {username}
Password: {password}

FIRST LOGIN INSTRUCTIONS:
1. Download the mobile app
2. Enter your credentials
3. Change your password on first login (REQUIRED)
4. Complete your profile if needed
5. Start using the app

IMPORTANT SECURITY NOTICE:
- Keep your credentials confidential
- Change your password immediately after first login
- Never share your password with anyone
- If you forget your password, contact your administrator

What you can do with your account:
- Attendance tracking and punch in/out
- Expense submission and tracking
- Project assignments and details
- Vehicle and equipment access
- Task management and updates

Need Help?
Contact your administrator if you have any questions.

© {company_name} - All Rights Reserved
This is an automated email. Please do not reply to this message.
        """

        # Send email
        msg = Message(
            subject=f"Welcome to {company_name} - Your Login Credentials",
            recipients=[employee_email],
            html=html_body,
            body=text_body
        )

        mail.send(msg)
        print(f"✅ Welcome email sent to {employee_email}")
        return True

    except Exception as e:
        print(f"❌ Error sending welcome email to {employee_email}: {e}")
        return False
