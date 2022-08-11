import threading
import queue
from typing import Dict
import logging

from handlers.misc.singleton import Singleton
from nodes import nodeFactory

logger = logging.getLogger(__name__)


@Singleton
class WorkerQueue:
    def __init__(self):
        self.q = queue.Queue()
        # Turn-on the worker thread.
        threading.Thread(target=self.worker, daemon=True).start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.q.join()

    def newJob(self, config: Dict[str, any]):
        self.q.put(config)

    def worker(self):
        while True:
            config = self.q.get()
            logger.info(f'Working on {config}')
            node = nodeFactory.getNode(config)
            node.execute()
            logger.info(f'Finished {config}')
            self.q.task_done()
