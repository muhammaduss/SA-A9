import os
import smtplib
import json
import logging
import sys
import time

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pika.exceptions import AMQPConnectionError
from pika import BlockingConnection, ConnectionParameters

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s | publisher | %(levelname)s | %(message)s",
)


connection_parameters = ConnectionParameters(host="rabbitmq", port=5672)

def wait_for_rabbitmq():
    while True:
        try:
            connection = BlockingConnection(connection_parameters)
            connection.close()
            logging.info('connection with rabbitmq established..')
            break
        except AMQPConnectionError:
            logging.info("Waiting for RabbitMQ...")
            time.sleep(5)

    
def process_message(ch, method, properties, body: bytes):
    message = json.loads(body)
    logging.info(
        f'''Consumer info: Received message from user: "{message['user_alias']}"'''
        f''' a message: "{message['message']}"'''
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)

    email_message = (
        f"From user: {message['user_alias']}\n" f"Message: {message['message']}"
    )

    send_email(email_message)
    # logging.info(email_message)


def send_email(message):
    from_m = os.getenv("FROM")
    to_m = os.getenv("TO")
    password = os.getenv("PASS")
    logging.info("From: %s, To: %s", from_m, to_m)
    msg = MIMEMultipart()
    msg["From"] = from_m
    msg["To"] = to_m
    msg["Subject"] = "Testing"

    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.set_debuglevel(1)
        server.starttls()
        server.login(from_m, password)
        text = msg.as_string()
        server.sendmail(from_m, to_m, text)
        server.quit()
        logging.info("Send email")
    except Exception as e:
        logging.info(f"Error {e}")


def consumer():
    with BlockingConnection(connection_parameters) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="messages_publisher")
            ch.basic_consume(
                queue="messages_publisher", on_message_callback=process_message
            )
            logging.info("waiting for messages...")
            ch.start_consuming()


if __name__ == "__main__":
    wait_for_rabbitmq()
    consumer()
