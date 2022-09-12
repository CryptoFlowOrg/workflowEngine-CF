import json
import threading

from nodes.nodeFactory import getNode
from workers.workerQueue import WorkerQueue
import logging


logging.basicConfig(level=logging.DEBUG)


def main(workflow_name: str):
    workflow = {}
    with open(f"./src/workflow/{workflow_name}.json", "r+") as f:
        workflow = json.loads(f.read())
    # We are just initializing the worker queue here
    WorkerQueue.instance()

    root = getNode(workflow["root"])
    root.execute()


if __name__ == '__main__':
    main("ScanUniswapForNewPairsAndTweet")
