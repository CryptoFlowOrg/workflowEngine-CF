import boto3
import logging
from typing import Any
from datetime import datetime

from models.config.properties.actions.template import Template
from nodes.baseNode import BaseNode
from workers.workerQueue import WorkerQueue
import json


logger = logging.getLogger(__name__)


class WriteToS3(BaseNode):
    event = None
    origin = None
    destination = None
    bucket = None

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.event = self.step["event"]
        _destination = Template(self.step["destination"])
        _destination.transform()
        _destination.render(self.event)
        if _destination.isValid():
            self.destination = _destination
        _origin = Template(self.step["origin"])
        _origin.transform()
        _origin.render(self.event)
        if _origin.isValid():
            self.origin = _origin
        _bucket = Template(self.step["bucket"])
        _bucket.transform()
        _bucket.render(self.event)
        if _bucket.isValid():
            self.bucket = _bucket

    def execute(self):
        s3 = boto3.resource('s3')
        s3.Object(self.bucket.rendered, self.destination.rendered).put(Body=open(self.origin.rendered, 'rb'))
        self.next_step()

    def isValid(self):
        if self.origin is None or \
                self.destination is None or \
                self.bucket is None or \
                self.event is None:
            return False
        return True

    def next_step(self) -> None:
        queue = WorkerQueue.instance()
        for step in self.next_steps:
            step.update({
                "event": self.event
            })
            queue.newJob(step)
            logger.info(f"Event writen to file {self.destination} and sent it to step: {step['node']}")
