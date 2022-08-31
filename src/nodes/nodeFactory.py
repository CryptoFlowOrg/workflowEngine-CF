from nodes.actions.writeToFile import WriteToFile
from nodes.actions.compute import Compute
from nodes.actions.matPlotLib import MatPlotLib
from nodes.actions.tweet import Tweet
from nodes.actions.writeToS3 import WriteToS3
from nodes.listeners.EVMMonitor import EVMMonitor
import logging

from nodes.actions.condenser import Condenser

logger = logging.getLogger(__name__)


def getNode(config: str):
    node = None

    if config["node"] == "EVMMonitor":
        node = EVMMonitor(config)
    if config["node"] == "tweet":
        node = Tweet(config)
    if config["node"] == "condenser":
        node = Condenser(config)
    if config["node"] == "compute":
        node = Compute(config)
    if config["node"] == "MatPlotLib":
        node = MatPlotLib(config)
    if config["node"] == "writeToFile":
        node = WriteToFile(config)
    if config["node"] == "writeToS3":
        node = WriteToS3(config)

    if node is None:
        message = f"Node type does not exist for config\n {config}"
        logger.exception(message)
        raise Exception(message)

    node.transform()
    if not node.isValid():
        message = f"Node config is invalid {config}"
        logger.exception(message)
        raise Exception(message)
    return node
