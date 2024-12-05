from pika import BlockingConnection, ConnectionParameters

connection_parameters = ConnectionParameters(
    host='localhost',
    port=5672
)


def main():
    with BlockingConnection(connection_parameters) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue='messages')

            ch.basic_publish(
                exchange="",
                routing_key="messages",
                body="Hello RabbitMQ!"
            )

            print('message sent')

if __name__ == '__main__':
    main()