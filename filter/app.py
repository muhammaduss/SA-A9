from pika import BlockingConnection, ConnectionParameters

connection_parameters = ConnectionParameters(
    host='localhost',
    port=5672
)


def process_message(ch, method, properties, body: bytes):
    message = body.decode()
    print(
        'Consumer info: Received message: ' +
        f'"{message}" from User-Facing service')

    ch.basic_ack(delivery_tag=method.delivery_tag)

    producer(ch, message)


def producer(ch, message):
    if ("bird-watching" in message or "ailurophobia" in message
            or "mango" in message):
        print("Producer info: Stop-word detected, " +
              "message won't be send further\n")
    else:
        ch.queue_declare(queue='messages_scream')
        ch.basic_publish(
            exchange="",
            routing_key="messages_scream",
            body=message
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
    consumer()
