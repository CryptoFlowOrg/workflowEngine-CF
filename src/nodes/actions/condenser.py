import logging
from typing import Any

from nodes.baseNode import BaseNode
from workers.workerQueue import WorkerQueue


global_events = []
logger = logging.getLogger(__name__)


class Condenser(BaseNode):
    events = 0

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.events = self.step["events"]

    def execute(self):
        global global_events
        global_events.append({
            "event_id": self.step["event"]["transactionHash"],
            "event": self.step["event"]
        })
        if len(global_events) == self.events:
            self.next_step()

    def isValid(self):
        return True
    
    def next_step(self) -> None:
        global global_events
        queue = WorkerQueue.instance()
        for step in self.next_steps:
            step.update({
                "event": global_events[:]
            })
            global_events = []
            queue.newJob(step)
            logger.info(f"We have just collected {self.events} and sent it to step: {step['node']}")