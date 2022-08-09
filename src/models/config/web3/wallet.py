from models.config.baseConfigModel import BaseConfigModel
from web3 import Web3


class WalletConfigModel(BaseConfigModel):
    web3_client = None
    chain_id = None
    private_key = None
    executor_wallet = None
    network_url = None
    gas = 3000000

    def transform(self):
        self.chain_id = self.raw['chain_id']
        self.private_key = self.raw['private_key']
        self.executor_wallet = self.raw['executor_wallet']
        self.network_url = self.raw['network_url']
        self.gas = self.raw.get('gas', self.gas)

        self.web3_client = Web3(Web3.HTTPProvider(self.network_url))
        self.web3_client.eth.account.from_key(self.private_key)

    def isValid(self) -> bool:
        if self.web3_client is None or \
                self.chain_id is None or \
                self.private_key is None or \
                self.executor_wallet is None or \
                self.network_url is None or \
                self.gas is None:
            return False
        return True

    def get_tx_args(self) -> dict[str, int | str]:
        nonce = self.web3_client.eth.get_transaction_count(self.executor_wallet)
        return {
            'chainId': self.get_chain_id(),
            'gas': self.gas,
            'gasPrice': self.web3_client.toWei('5', 'gwei'),
            'nonce': nonce
        }
