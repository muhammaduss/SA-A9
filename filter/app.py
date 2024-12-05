print("run docker service")
import json
import time
from pika import BlockingConnection, ConnectionParameters
from pika.exceptions import AMQPConnectionError

connection_parameters = ConnectionParameters(
    host='rabbitmq',
    port=5672
)

def wait_for_rabbitmq():
    while True:
        try:
            connection = BlockingConnection(connection_parameters)
            connection.close()
            print("RabbitMQ is ready!")
            break
        except AMQPConnectionError:
            print("Waiting for RabbitMQ...")
            time.sleep(5)



def process_message(ch, method, properties, body: bytes):
    message = json.loads(body)
    print(f'''Consumer info: Received message from user: "{message['user_alias']}"'''
          f''' a message: "{message['message']}"''')

    ch.basic_ack(delivery_tag=method.delivery_tag)

    producer(ch, message)


def producer(ch, message):
    if ("bird-watching" in message['message'] or
            "ailurophobia" in message['message'] or
            "mango" in message['message']):
        print("Producer info: Stop-word detected, " +
              "message won't be send further\n")
    else:
        ch.queue_declare(queue='messages_scream')
        ch.basic_publish(
            exchange="",
            routing_key="messages_scream",
            body=json.dumps(message)
        )
        print("Producer info: Message sent to SCREAMING service\n")


def consumer():
    with BlockingConnection(connection_parameters) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue='messages')
            ch.basic_consume(
                queue="messages",
                on_message_callback=process_message
            )
            print('waiting for messages...')
            ch.start_consuming()


if __name__ == '__main__':
    wait_for_rabbitmq()
    consumer()
