import random
import string

def generate_token():
    prefix = "EAAAU"
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=80))
    token = prefix + random_part
    return token
