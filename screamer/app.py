import logging
import sys
import time
import json

from pika import BlockingConnection, ConnectionParameters
from pika.exceptions import AMQPConnectionError

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s | screamer | %(levelname)s | %(message)s")

connection_parameters = ConnectionParameters(
    host='rabbitmq',
    port=5672
)

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
    logging.info(f'''Consumer info: Received message from user: "{message['user_alias']}"'''
                 f''' a message: "{message['message']}"''')

    ch.basic_ack(delivery_tag=method.delivery_tag)

    producer(ch, message)


def producer(ch, message):
    message['message'] = message['message'].upper()
    ch.queue_declare(queue='messages_publisher')
    ch.basic_publish(
        exchange="",
        routing_key="messages_publisher",
        body=json.dumps(message)
    )
    logging.info("Producer info: Uppercased message sent to Publisher service\n")


def consumer():
    with BlockingConnection(connection_parameters) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue='messages_scream')
            ch.basic_consume(
                queue="messages_scream",
                on_message_callback=process_message
            )
            logging.info('waiting for messages...')
            ch.start_consuming()


if __name__ == '__main__':
    wait_for_rabbitmq()
    consumer()
