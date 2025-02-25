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

# # Example usage
# if __name__ == "__main__":
#     email_backend = EmailBackend('smtp.example.com', 587, 'your_username', 'your_password')
#     email_backend.send_email('from@example.com', 'to@example.com', 'Test Subject', 'This is a test email.')

import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils.functional import cached_property
 
class EmailBackend(SMTPBackend):
 
    @cached_property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
          ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
          ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
          return ssl_context
      
        else:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context