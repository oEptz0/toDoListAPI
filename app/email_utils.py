import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, content: str):
    try:
        smtp_host = os.getenv('EMAIL_HOST')
        smtp_port = os.getenv('EMAIL_PORT')
        smtp_user = os.getenv('EMAIL_USER')
        smtp_password = os.getenv('EMAIL_PASSWORD')

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html'))

        server.send_message(msg)
        server.quit()

        return "Email sent successfully"
    
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return None
