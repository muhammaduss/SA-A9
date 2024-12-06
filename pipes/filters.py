from __future__ import annotations

from dataclasses import dataclass, field

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import json
from multiprocessing import Process, Queue
from abc import ABC, abstractmethod

import os
import smtplib
import sys
import logging

from dotenv import load_dotenv

load_dotenv()




@dataclass
class Filter(ABC):
    input_queue: Queue = field(default_factory=Queue, repr=False)
    output_queue: Queue = field(default_factory=Queue, repr=False)

    @abstractmethod
    def apply(self, message: str) -> str | None:
        pass

    def pipe(self, filter: Filter):
        self.output_queue = filter.input_queue
        return filter

    def run(self):
        while True:
            msg = self.input_queue.get()
            if msg is None:
                self.output_queue.put(None)
                break
            transformed = self.apply(msg)
            if transformed and self.output_queue is not None:
                self.output_queue.put(transformed)


class FilterFilter(Filter):
    def apply(self, message):

        if (
            "bird-watching" in message
            or "ailurophobia" in message
            or "mango" in message
        ):
            logging.info(
                "FilterFilter info: Stop-word detected, "
                + "message won't be send further\n"
            )
            return None
        return message


class Screamer(Filter):
    def apply(self, message):
        return message.upper()


class Publisher(Filter): 
    def apply(self, message):
        from_m = os.getenv("FROM")
        list_mails = os.getenv("LIST_MAILS")
        password = os.getenv("PASS")
        try:
            email_addresses = json.loads(list_mails)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing LIST_MAILS: {e}")
            return

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
            server.set_debuglevel(1)
            server.starttls()
            server.login(from_m, password)
            for i in email_addresses: 
                msg = MIMEMultipart()
                msg["From"] = from_m
                msg["To"] = i 
                msg["Subject"] = "Testing"    
                logging.info("From: %s, To: %s", from_m, i)
                msg.attach(MIMEText(message, "plain"))
                text = msg.as_string()
                server.sendmail(from_m, i, text)
                logging.info("Send email")
            server.quit()
        except Exception as e:
            logging.info(f"Error {e}")

        return message
        
