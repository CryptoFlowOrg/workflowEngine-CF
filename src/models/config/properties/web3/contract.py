from models.config.baseConfigModel import BaseConfigModel
from web3 import Web3
import json


class ContractConfigModel(BaseConfigModel):
    abi = None
    address = None
    event_name = None
    filters = [] # optional

    def transform(self):
        self.abi = self.raw['ABI']
        self.address = Web3.toChecksumAddress(self.raw['address'])
        self.event_name = self.raw['event_name']
        if "filters" in self.raw:
            self.filters = self.raw["filters"]

    def isValid(self) -> bool:
        if self.abi is None or \
                self.address is None or \
                self.event_name is None:
            return False
        return True
