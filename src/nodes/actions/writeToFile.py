import logging
from typing import Any
from datetime import datetime

from models.config.properties.actions.template import Template
from nodes.baseNode import BaseNode
from workers.workerQueue import WorkerQueue
import json


logger = logging.getLogger(__name__)


class WriteToFile(BaseNode):
    event = None
    destination = None

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.event = self.step["event"]
        _destination = Template(self.step["destination"])
        _destination.transform()
        _destination.render(self.event)
        if _destination.isValid():
            self.destination = _destination

    def execute(self):
        with open(self.destination.rendered, "w+") as f:
            f.write(json.dumps(self.event))
        self.next_step(self.event)

    def isValid(self):
        if self.destination is None or \
                self.event is None:
            return False
        return True

    def next_step(self, processed) -> None:
        queue = WorkerQueue.instance()
        for step in self.next_steps:
            step.update({
                "event": self.event
            })
            queue.newJob(step)
            logger.info(f"Event writen to file {self.destination} and sent it to step: {step['node']}")
