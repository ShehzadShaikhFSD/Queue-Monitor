import pika
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()
 
# AMQP connection settings
AMQP_URL = os.getenv("AMQP_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")
 
# SendGrid SMTP settings
SENDGRID_SMTP = os.getenv("SENDGRID_SMTP")
SENDGRID_PORT = os.getenv("SENDGRID_PORT ")
SENDGRID_USER = os.getenv("SENDGRID_USER")
SENDGRID_PASSWORD = os.getenv("SENDGRID_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
 
def get_queue_message_count():
    params = pika.URLParameters(AMQP_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    queue = channel.queue_declare(queue=QUEUE_NAME, passive=True)
    message_count = queue.method.message_count
    connection.close()
    return message_count
 
def send_email_alert(queue_length):
    subject = f"CloudAMQP ALERT: {QUEUE_NAME} has {queue_length} items"
    body = (f"Queue '{QUEUE_NAME}' currently has {queue_length} items. "
            "This may indicate it is stuck. "
            "Please visit the CloudAMQP dashboard to confirm and investigate.")
 
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
 
    with smtplib.SMTP_SSL(SENDGRID_SMTP, SENDGRID_PORT) as server:
        server.login(SENDGRID_USER, SENDGRID_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
 
if __name__ == "__main__":
    queue_length = get_queue_message_count()
    print(f"Queue '{QUEUE_NAME}' has {queue_length} messages.")
    # if queue_length > 10:
    #     send_email_alert(queue_length)
    #     print("Alert sent.")
    if queue_length == 0:
        send_email_alert(queue_length)
        print("Alert sent.")
#