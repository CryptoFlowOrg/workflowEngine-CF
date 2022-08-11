from nodes.actions.tweet import Tweet
from nodes.listeners.EVMMonitor import EVMMonitor
import logging

logger = logging.getLogger(__name__)


def getNode(config: str):
    node = None

    if config["node"] == "EVMMonitor":
        node = EVMMonitor(config)
    if config["node"] == "tweet":
        node = Tweet(config)

    if node is None:
        message = f"Node type does not exist for config\n {config}"
        logger.exception(message)
        raise Exception(message)

    node.transform()
    return node
