import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



sender_email = 'v-maria77@hotmail.com'
sender_password = 'Phong24052001'
smtp_server = 'smtp-mail.outlook.com'
smtp_port = 587  # Change this if your SMTP server uses a different port
subject = 'Mã thay đổi mật khẩu EduSmart'
def send_email(recipient_email, body):
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach body
        msg.attach(MIMEText(body, 'plain'))

        # Start the SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)

        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        print('Email sent successfully!')
        return True

    except Exception as e:
        print(f'Error: {e}')
        return False

    finally:
        server.quit()  # Close the SMTP session
        

def email_validation(email):
    import re
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    return False

