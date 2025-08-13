# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# class EmailBackend:
#     def __init__(self, smtp_server, smtp_port, username, password):
#         self.smtp_server = smtp_server
#         self.smtp_port = smtp_port
#         self.username = username
#         self.password = password

#     def send_email(self, from_addr, to_addr, subject, body):
#         # Create the email message
#         msg = MIMEMultipart()
#         msg['From'] = from_addr
#         msg['To'] = to_addr
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'plain'))

#         # Connect to the SMTP server and send the email
#         try:
#             server = smtplib.SMTP(self.smtp_server, self.smtp_port)
#             server.starttls()
#             server.login(self.username, self.password)
#             server.sendmail(from_addr, to_addr, msg.as_string())
#             server.quit()
#             print("Email sent successfully")
#         except Exception as e:
#             print(f"Failed to send email: {e}")

# Example usage
# if __name__ == "__main__":
#     email_backend = EmailBackend('smtp.example.com', 587, 'your_username', 'your_password')
#     email_backend.send_email('from@example.com', 'to@example.com', 'Test Subject', 'This is a test email.')



# import ssl
# from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
# from django.utils.functional import cached_property
 
# class EmailBackend(SMTPBackend):
 
#     @cached_property
#     def ssl_context(self):
#         if self.ssl_certfile or self.ssl_keyfile:
#           ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
#           ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
#           return ssl_context
      
#         else:
#             ssl_context = ssl.create_default_context()
#             ssl_context.check_hostname = False
#             ssl_context.verify_mode = ssl.CERT_NONE
#             return ssl_context

import resend
from jinja2 import Environment, FileSystemLoader
import os
from roothub_project import settings

base_dir = settings.BASE_DIR
template_dir = os.path.join(base_dir, "templates", "emails")
env = Environment(loader=FileSystemLoader(template_dir))

EMAIL_CRED = settings.RESEND_EMAIL
resend.api_key = settings.RESEND_API_KEY

def render_email_template(template_name):
    """Render an email template with context."""
    template = env.get_template(template_name)
    return template.render()

def send_email(to_email: str, subject: str, body: str):
    """Sends an email."""
    try:
        params : resend.Emails.SendParams = {
            "from": EMAIL_CRED,
            "to": [to_email],
            "subject": subject,
            "html": body
        }
        
        email: resend.Email = resend.Emails.send(params)
        return {
            "status": "success",
            "message": f"Email sent successfully to {email}.",
        }
    except Exception as e:
        # return {
        #     "status": "error",
        #     "message": f"Failed to send email to {to_email}. Error: {str(e)}",
        # }
        print(e)

def send_forgot_password_email(token, email):
    subject = "Password Reset"
    link = f"{settings.FORGET_PASSWORD_LINK}?token={token}"
    html_body = render_email_template("forgot-password.html")
    return send_email(to_email=email, subject=subject, body=html_body)