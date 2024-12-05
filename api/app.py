from fastapi import FastAPI
from .schemas import ReceiveMessage
from pika import BlockingConnection, ConnectionParameters

connection_parameters = ConnectionParameters(
    host='localhost',
    port=5672
)

app = FastAPI(title="User-Facing REST API Documentation")


@app.post("/recieve")
async def post_recieve_message(data: ReceiveMessage):
    with BlockingConnection(connection_parameters) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue='messages')
            ch.basic_publish(
                exchange="",
                routing_key="messages",
                body=data.message
            )
            print('message sent')
