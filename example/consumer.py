from pika import BlockingConnection, ConnectionParameters

connection_parameters = ConnectionParameters(
    host='localhost',
    port=5672
)
def process_message(*args):
    for arg in args:
        print(arg, '\n\n')


def main():
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
    main()