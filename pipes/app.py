from contextlib import asynccontextmanager
import logging
import sys
import json
import datetime
from fastapi import FastAPI
from multiprocessing import Process

from schemas import ReceiveMessage
from filters import FilterFilter, Screamer, Publisher

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s | pipe | %(levelname)s | %(message)s",
)

logging.info('start up')

@asynccontextmanager
async def lifespan(app: FastAPI):
    filter_filter = FilterFilter()
    screamer = Screamer()
    publisher = Publisher()
    filter_filter.pipe(screamer).pipe(publisher)

    filter_process = Process(target=filter_filter.run, daemon=True)
    screamer_process = Process(target=screamer.run, daemon=True)
    publisher_process = Process(target=publisher.run, daemon=True)

    filter_process.start()
    screamer_process.start()
    publisher_process.start()

    app.state.pipeline_start = filter_filter
    app.state.processes = [filter_process, screamer_process, publisher_process]

    yield
    app.state.pipeline_start.input_queue.put(None)
    for p in app.state.processes:
        p.join()


app = FastAPI(title="User-Facing REST API Documentation", lifespan=lifespan)


@app.post("/recieve")
async def post_recieve_message(data: ReceiveMessage):
    logging.info(f"Message sent at: {datetime.datetime.now()}")
    app.state.pipeline_start.input_queue.put(data.message)
    return {"status": "message queued"}
