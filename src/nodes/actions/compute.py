import logging
from typing import Any
from datetime import datetime
from nodes.baseNode import BaseNode
from workers.workerQueue import WorkerQueue


logger = logging.getLogger(__name__)


def walletBalance(wallet: str, decimals: int, events: list[Any]) -> list[Any]:
    s = 0
    data = {}
    i = 0
    while i < len(events):
        if events[i]["blockNumber"] == events[i+1]["blockNumber"]:
            _out = events[i]["args"]
            _in = events[i + 1]["args"]

            diff = _in["value"] - _out["value"]
            s += diff
            data[events[i]["block_when"]] = s / (10 ** decimals)
            i += 2
        else:
            i += 1
    return data


class Compute(BaseNode):
    flavour = None
    event = None
    wallet = None
    decimals = None

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.flavour = self.step["flavour"]
        self.event = self.step["event"]
        self.wallet = self.step["wallet"]
        self.decimals = self.step["decimals"]

    def execute(self):
        op = None
        if self.flavour == "walletBalance":
            op = walletBalance
        _event = op(self.wallet, self.decimals, self.event)
        self.next_step(_event)

    def isValid(self):
        if self.flavour is None or \
                self.wallet is None or \
                self.decimals is None:
            return False
        return True

    def next_step(self, processed) -> None:
        queue = WorkerQueue.instance()
        for step in self.next_steps:
            step.update({
                "event": {
                    "processed": processed,
                    "raw": self.event
                }
            })
            queue.newJob(step)
            logger.info(f"We have just computed {self.flavour} and sent it to step: {step['node']}")
