
import requests
api_key = ''
sender_email = ''

def send_email(recipient_email, link):
    try:
        # Tạo tiêu đề và nội dung email
        subject = "Reset Your Password"
        body = f"Please click on the link to reset your password: {link}, \n\nThis link will expire in 5 minutes."

        # Định dạng JSON cho API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "from": {"email": sender_email},
            "to": [{"email": recipient_email}],
            "subject": subject,
            "text": body
        }

        # URL của MailerSend API
        url = "https://api.mailersend.com/v1/email"

        # Gửi request POST đến MailerSend
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 202:  # MailerSend returns 202 for accepted messages
            print('Email sent successfully!')
            return True
        else:
            print('Failed to send email:', response.text)
            return False

    except Exception as e:
        print(f'Error: {e}')
        return False

        
def email_validation(email):
    import re
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    return False

def generate_code():
    import random
    # random code 6 number have char + number (0-9, a-z, A-Z)
    code = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))   
    return code

