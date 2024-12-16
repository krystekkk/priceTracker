from email.mime.text import MIMEText
from email.mime.image import MIMEImage 
from email.mime.application import MIMEApplication 
from email.mime.multipart import MIMEMultipart
from config import EMAIL_HOST, EMAIL_PASSWORD, EMAIL_CLIENT
import smtplib


def send_email(product_url, price, limit_price):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(EMAIL_HOST, EMAIL_PASSWORD)

    message = MIMEMultipart()
    message['Subject'] = 'Price of your product decreased'
    message.attach(MIMEText(
        f'The price of your product of interest decreased below {limit_price} PLN and costs now {price} PLN.\n'
        f'Check your product: {product_url}'
    ))

    to = EMAIL_CLIENT
    smtp.sendmail(from_addr=EMAIL_HOST, to_addrs=to, msg=message.as_string())
    smtp.quit()
