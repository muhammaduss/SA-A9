import json
import logging
import sys
import datetime
from fastapi import FastAPI
from schemas import ReceiveMessage
from pika import BlockingConnection, ConnectionParameters

connection_parameters = ConnectionParameters(
    host='rabbitmq',
    port=5672
)

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s | publisher | %(levelname)s | %(message)s",
)


app = FastAPI(title="User-Facing REST API Documentation")


@app.post("/recieve")
async def post_recieve_message(data: ReceiveMessage):
    logging.info(f'Message recieved at: {datetime.datetime.now()}')
    with BlockingConnection(connection_parameters) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue='messages')
            ch.basic_publish(
                exchange="",
                routing_key="messages",
                body=json.dumps(
                    {'user_alias': data.user_alias, 'message': data.message})
            )
            logging.info('Message sent to filter service')
