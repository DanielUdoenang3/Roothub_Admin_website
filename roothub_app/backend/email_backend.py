import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
# from roothub_project import settings
from django.conf import settings
from django.template.loader import render_to_string

def send_email(to_email, subject, body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = formataddr(("Roothub", settings.EMAIL_HOST_USER))
    msg['To'] = Header(to_email, 'utf-8')
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    try:
        if settings.EMAIL_PORT == 465:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, 587)
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        raise # Re-raise the exception for the caller to handle

def generate_forgot_password_email(token: str, email: str):
    """Generate forgot password email body using Django templates."""
    link = f"{settings.FORGET_PASSWORD_LINK}/reset_password/{token}/"
    context = {
        "email": email,
        "link": link
    }
    return render_to_string("emails/forgot-password.html", context)

def generate_login_email(first_name, last_name, schoolname, EMAIL_HOST_USER, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB):
    """Generate Login email body"""
    context = {
        "first_name" : first_name,
        "last_name":last_name,
        "schoolname":schoolname,
        "EMAIL_HOST_USER":EMAIL_HOST_USER,
        "SCHOOL_NUM1":SCHOOL_NUM1,
        "SCHOOL_NUM2":SCHOOL_NUM2,
        "SCHOOL_WEB":SCHOOL_WEB,
    }
    return render_to_string("emails/login.html", context)

def generate_add_trainee_email(first_name, middle_name, last_name, username, email, password, schoolname, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, ALOWED_HOST_ONLINE):
    context = {
        "first_name" : first_name,
        "middle_name":middle_name,
        "last_name":last_name,
        "username":username,
        "email":email,
        "password":password,
        "schoolname":schoolname,
        "SCHOOL_NUM1":SCHOOL_NUM1,
        "SCHOOL_NUM2":SCHOOL_NUM2,
        "SCHOOL_WEB":SCHOOL_WEB,
        "ALOWED_HOST_ONLINE":ALOWED_HOST_ONLINE,
    }
    return render_to_string("emails/add_trainee.html", context)

def generate_add_trainer_email(first_name, middle_name, last_name, username, email, password, schoolname, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, ALOWED_HOST_ONLINE):
    context = {
        "first_name" : first_name,
        "middle_name":middle_name,
        "last_name":last_name,
        "username":username,
        "email":email,
        "password":password,
        "schoolname":schoolname,
        "SCHOOL_NUM1":SCHOOL_NUM1,
        "SCHOOL_NUM2":SCHOOL_NUM2,
        "SCHOOL_WEB":SCHOOL_WEB,
        "ALOWED_HOST_ONLINE":ALOWED_HOST_ONLINE,
    }
    return render_to_string("emails/add_trainer.html", context)


def generate_assign_trainer_email(trainer_name, schoolname, assignments, ALOWED_HOST_ONLINE):
    """
    Generate assignment email for trainer.
    assignments: list of dicts [{course_name: str, levels: [str]}]
    """
    context = {
        "trainer_name": trainer_name,
        "schoolname": schoolname,
        "assignments": assignments,
        "ALOWED_HOST_ONLINE": ALOWED_HOST_ONLINE,
    }
    return render_to_string("emails/assign_trainer.html", context)

def send_forgot_password_email(token: str, email: str):
    """Sends a forgot password email."""
    subject = "Password reset"
    body = generate_forgot_password_email(token=token, email=email)
    return send_email(to_email=email, subject=subject, body=body)

def send_login_body(first_name, last_name, schoolname, EMAIL_HOST_USER, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, email):
    """Sends a login email"""
    subject = "Login Detected"
    body = generate_login_email(first_name, last_name, schoolname, EMAIL_HOST_USER, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB)
    return send_email(to_email=email, subject=subject, body=body)

def send_add_trainee(first_name, middle_name, last_name, username, password, schoolname, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, ALOWED_HOST_ONLINE, email):
    """
    Sends a welcome email to a newly added trainee.
    """
    subject = f"Welcome to {schoolname}"
    body = generate_add_trainee_email(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password,
        schoolname=schoolname,
        SCHOOL_NUM1=SCHOOL_NUM1,
        SCHOOL_NUM2=SCHOOL_NUM2,
        SCHOOL_WEB=SCHOOL_WEB,
        ALOWED_HOST_ONLINE=ALOWED_HOST_ONLINE
    )
    return send_email(to_email=email, subject=subject, body=body)

def send_add_trainer(first_name, middle_name, last_name, username, password, schoolname, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, ALOWED_HOST_ONLINE, email):
    """
    Sends a welcome email to a newly added trainer.
    """
    subject = f"Welcome to {schoolname}"
    body = generate_add_trainer_email(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password,
        schoolname=schoolname,
        SCHOOL_NUM1=SCHOOL_NUM1,
        SCHOOL_NUM2=SCHOOL_NUM2,
        SCHOOL_WEB=SCHOOL_WEB,
        ALOWED_HOST_ONLINE=ALOWED_HOST_ONLINE
    )
    return send_email(to_email=email, subject=subject, body=body)


def send_assign_trainer(trainer, schoolname, assignments, ALOWED_HOST_ONLINE, email):
    """
    Send assignment email to trainer.
    trainer: Trainer object or name string
    assignments: list of dicts [{course_name: str, levels: [str]}]
    """
    trainer_name = trainer.trainer_name.first_name + " " + trainer.trainer_name.last_name if hasattr(trainer, 'trainer_name') else str(trainer)
    subject = f"New Course & Level Assignment at {schoolname}"
    body = generate_assign_trainer_email(trainer_name, schoolname, assignments, ALOWED_HOST_ONLINE)
    return send_email(to_email=email, subject=subject, body=body)

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

# from django.template.loader import render_to_string
# import resend
# from roothub_project import settings

# EMAIL_CRED = settings.RESEND_EMAIL
# resend.api_key = "re_EBiZJgLh_JaEsrfcDpawxUpzAxvx2mLuE"

# import resend

# resend.api_key = "re_EBiZJgLh_JaEsrfcDpawxUpzAxvx2mLuE"

# r = resend.Emails.send({
#   "from": "onboarding@resend.dev",
#   "to": "danieludoenangjnr33@gmail.com",
#   "subject": "Hello World",
#   "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
# })

# def send_forgot_password_email(email):

#   """Sends an email."""
#         # params = {
#         #     "from": "Daniel <no-reply@yourdomain.com>",
#         #     "to": email,
#         #     "subject": "Test Email",
#         #     "html": "<p>Hello from Resend!</p>"
#         # }
        
#   email = resend.Emails.send(
#     {
#     "from": "Daniel <no-reply@yourdomain.com>",
#     "to": email,
#     "subject": "Test Email",
#     "html": "<p>Hello from Resend!</p>"
#     }
#   )
#   if email:
#     print({
#         "status": "success",
#         "message": f"Email sent successfully to {email}.",
#     })
#   else:
#     print("9Failed to send email.")

# def generate_forgot_pwd_email(token: str, email: str):
#     """Generate forgot password email body using Django templates."""
#     link = f"{settings.FORGET_PASSWORD_LINK}?token={token}"
#     context = {
#         "email": email,
#         "link": link
#     }
#     return render_to_string("emails/forgot-password.html", context)

# def send_forgot_password_email(token: str, email: str):
#     """Resets user's password."""
#     subject = "Password reset"
#     body = generate_forgot_pwd_email(token=token, email=email)
#     send_email(to_email=email, subject=subject, body=body)

# def send_forgot_password_email(email):
#   """Sends an email."""
#   try:
#     email_response = resend.Emails.send({
#         "from": "Roothub@resend.dev",
#         "to": [email],
#         "subject": "Test Email",
#         "html": "<p>Hello from Resend!</p>"
#     })
#     print(email_response)
#   except Exception as e:
#     print("Resend error:", e)
