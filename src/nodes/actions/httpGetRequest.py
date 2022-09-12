import logging
from typing import Any
from datetime import datetime

from models.config.properties.actions.template import Template
from nodes.baseNode import BaseNode
from workers.workerQueue import WorkerQueue
import json
import requests


logger = logging.getLogger(__name__)


class HttpGetRequest(BaseNode):
    event = None
    url = None

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.event = self.step["event"]
        _url = Template(self.step["url"])
        _url.transform()
        _url.render(self.event)
        if _url.isValid():
            self.url = _url

    def execute(self):
        response = None
        r = requests.get(self.url.rendered)
        if r.status_code == 200:
            if "application/json" in r.headers['content-type']:
                response = r.json()
            else:
                response = r.text
            if "restResponse" not in self.event:
                self.event["restResponse"] = []
            self.event["restResponse"].append(response)
            self.next_step()
        else:
            logger.info(f"Error calling url: {self.url} :: {r.status_code}\n{r.text}")

    def isValid(self):
        if self.url is None or \
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
            logger.info(f"Event collected from url: {self.url} and sent it to step: {step['node']}")
