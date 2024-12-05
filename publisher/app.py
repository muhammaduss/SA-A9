import smtplib 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 

import os
from dotenv import load_dotenv
load_dotenv()


print("tests")
def send_email (message): 
    from_m = os.getenv('FROM')
    to_m = os.getenv('TO')
    password = os.getenv('PASS')
    print(from_m, to_m, password)
    msg = MIMEMultipart()
    msg['From'] = from_m 
    msg['To'] = to_m 
    msg['Subject'] = "Testing"

    msg.attach(MIMEText(message, 'plain'))
    
    try: 
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10) 
        server.set_debuglevel(1) 
        server.starttls()
        server.login(from_m, password)
        text = msg.as_string()
        server.sendmail(from_m, to_m, text) 
        server.quit()
        print(f"Send email")
    except Exception as e: 
        print(f"Error {e}")
        
send_email("It is testing message")