import logging
from typing import Any
import matplotlib.pyplot as plt
from datetime import date

from models.config.properties.actions.matplotlibGraph import MatPlotLibGraph
from nodes.baseNode import BaseNode
from workers.workerQueue import WorkerQueue

logger = logging.getLogger(__name__)


class MatPlotLib(BaseNode):
    graph_config = None
    event = None

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.event = self.step["event"]
        _graph_config = MatPlotLibGraph(self.step["graph_config"])
        _graph_config.transform()
        _graph_config.render(self.event)
        if _graph_config.isValid():
            self.graph_config = _graph_config

    def execute(self):
        x = list(self.event["processed"].keys())
        y = list(self.event["processed"].values())
        plt.plot(x, y, marker=self.graph_config.marker, color=self.graph_config.color)
        plt.xlabel(self.graph_config.xlabel.rendered)
        plt.ylabel(self.graph_config.ylabel.rendered)
        plt.title(self.graph_config.title.rendered)
        plt.savefig(self.graph_config.destination_file)
        self.next_step()

    def isValid(self):
        if self.graph_config is None or \
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
            logger.info(f"We have rendered a graph and moving to step: {step['node']}")
