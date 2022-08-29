from models.config.baseConfigModel import BaseConfigModel
from models.config.properties.actions.template import Template


class MatPlotLibGraph(BaseConfigModel):
    marker = None
    color = None
    destination_file = None
    xlabel = None
    ylabel = None
    title = None

    def transform(self):
        self.marker = self.raw["marker"]
        self.color = self.raw["color"]
        self.destination_file = self.raw["destination_file"]
        _xlabel = Template(self.raw["xlabel"])
        _xlabel.transform()
        if _xlabel.isValid():
            self.xlabel = _xlabel
        _ylabel = Template(self.raw["ylabel"])
        _ylabel.transform()
        if _ylabel.isValid():
            self.ylabel = _ylabel
        _title = Template(self.raw["title"])
        _title.transform()
        if _title.isValid():
            self.title = _title

    def render(self, event):
        self.xlabel.render(event)
        self.ylabel.render(event)
        self.title.render(event)

    def isValid(self) -> bool:
        if self.marker is None or \
                self.color is None or \
                self.xlabel is None or \
                self.ylabel is None or \
                self.title is None or \
                self.destination_file is None:
            return False
        return True
