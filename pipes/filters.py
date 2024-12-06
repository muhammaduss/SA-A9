from __future__ import annotations
from dataclasses import dataclass, field
from multiprocessing import Process, Queue
from abc import ABC, abstractmethod
import sys


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
            if transformed:
                self.output_queue.put(transformed)


class FilterFilter(Filter):
    def apply(self, message):

        if (
            "bird-watching" in message
            or "ailurophobia" in message
            or "mango" in message
        ):
            print(
                "FilterFilter info: Stop-word detected, "
                + "message won't be send further\n"
            )
            return None
        return message
    
class Screamer(Filter):
    def apply(self, message):
        return message.upper()
    

class Publisher(Filter):
    ...