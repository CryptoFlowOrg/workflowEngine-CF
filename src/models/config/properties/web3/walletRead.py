from models.config.baseConfigModel import BaseConfigModel
from web3 import Web3


class WalletReadConfigModel(BaseConfigModel):
    web3_client = None
    chain_id = None
    network_url = None

    def transform(self):
        self.chain_id = self.raw['chain_id']
        self.network_url = self.raw['network_url']

        self.web3_client = Web3(Web3.HTTPProvider(self.network_url))

    def isValid(self) -> bool:
        if self.web3_client is None or \
                self.chain_id is None or \
                self.network_url is None:
            return False
        return True

