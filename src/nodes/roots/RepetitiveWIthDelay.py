from web3 import Web3

from handlers.web3.EventScanner import EventScanner
from models.config.properties.web3.contract import ContractConfigModel
from models.config.properties.web3.walletRead import WalletReadConfigModel
from nodes.baseNode import BaseNode
from workers.web3.EVMEventScannerProcessing import EVMEventScannerProcessing
import math
from web3.middleware import geth_poa_middleware
from time import sleep, time

from workers.workerQueue import WorkerQueue
import logging


logger = logging.getLogger(__name__)


class RepetitiveWIthDelay(BaseNode):
    sleep_duration = None

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.sleep_duration = self.step["sleep_duration"]

    def isValid(self) -> bool:
        if self.sleep_duration is None:
            return False
        return True

    def execute(self):
        while True:
            self.emitEvent({})
            logger.debug(f"Sleeping for {self.sleep_duration}s")
            sleep(self.sleep_duration)


    def emitEvent(self, event):
        queue = WorkerQueue.instance()
        for step in self.next_steps:
            step.update({
                "event": event
            })
            queue.newJob(step)
            logger.info(f"Workflow was been triggered and sent to step: {step['node']}")