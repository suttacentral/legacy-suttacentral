import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
    
import sc

def send(to, subject, from_address=None, text=None, html=None):
    msg = MIMEMultipart('alternative')
    
    msg['Subject'] = subject
    msg['From'] = from_address or sc.config.email['from']
    msg['To'] = to
    
    if text:
        msg.attach(MIMEText(text, 'plain'))
    if html:
        msg.attach(MIMEText(html, 'html'))

    username = sc.config.email['username']
    password = sc.config.email['password']
    
    smtp_server = sc.config.email['smtp_server']
    smtp_port = sc.config.email['smtp_port']
    
    s = smtplib.SMTP(smtp_server, smtp_port)
    s.login(username, password)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()
    

    
