from web3 import Web3

from handlers.web3.EventScanner import EventScanner
from models.config.properties.web3.contract import ContractConfigModel
from models.config.properties.web3.walletRead import WalletReadConfigModel
from nodes.baseNode import BaseNode
from workers.web3.EVMEventScannerProcessing import EVMEventScannerProcessing
import math
from web3.middleware import geth_poa_middleware
from time import sleep, time


class EVMMonitor(BaseNode):
    wallet = None
    contract = None

    def transform(self):
        _wallet = WalletReadConfigModel(self.step["wallet"])
        _wallet.transform()
        if _wallet.isValid():
            self.wallet = _wallet
        _contract = ContractConfigModel(self.step["contract"])
        _contract.transform()
        if _contract.isValid():
            self.contract = _contract

    def isValid(self) -> bool:
        if self.wallet is None or \
                self.contract is None:
            return False
        return True

    def execute(self):
        # provider = Web3.HTTPProvider(self.wallet.network_url)
        # Remove the default JSON-RPC retry middleware
        # as it correctly cannot handle eth_getLogs block range
        # throttle down.
        # provider.middlewares.clear()
        #
        # web3 = Web3(provider)
        self.wallet.web3_client.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Prepare stub ERC-20 contract object
        Contract = self.wallet.web3_client.eth.contract(abi=self.contract.abi)

        # Restore/create our persistent state
        state = EVMEventScannerProcessing(self.processEvent)

        scanner = EventScanner(
            web3=self.wallet.web3_client,
            contract=Contract,
            state=state,
            events=[Contract.events[self.contract.event_name]],
            filters={"address": self.contract.address},
            # How many maximum blocks at the time we request from JSON-RPC
            # and we are unlikely to exceed the response size limit of the JSON-RPC server
            max_chunk_scan_size=2000
        )

        state.end_chunk(scanner.get_suggested_scan_end_block())

        chain_reorg_safety_blocks = 10
        scanner.delete_potentially_forked_block_data(state.get_last_scanned_block() - chain_reorg_safety_blocks)

        while True:
            start_block = state.get_last_scanned_block()
            end_block = scanner.get_suggested_scan_end_block()
            t0 = time()
            while end_block - start_block < 10:
                sleep(5)
                start_block = state.get_last_scanned_block()
                end_block = scanner.get_suggested_scan_end_block()
            print(f"time waiting for new events {time() - t0} s")
            print(f"Scanning events from blocks {start_block} - {end_block}")
            t0 = time()
            # Run the scan
            scanner.scan(start_block, end_block, progress_callback=None)
            print(f"Completed scan from {start_block} to {end_block} in {time() - t0}s")
            state.end_chunk(end_block + 1)

    def processEvent(self, tx_id: str, args: dict[str, str]):
        print(tx_id, args)


if __name__ == '__main__':
    import json
    import logging
    logging.basicConfig(level=logging.DEBUG)

    wallet = {
        "chain_id": 0,
        "network_url": "https://polygon-rpc.com"
    }
    contract = {
        "abi": json.dumps([
            {
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "sender",
                        "type": "address"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "amount0In",
                        "type": "uint256"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "amount1In",
                        "type": "uint256"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "amount0Out",
                        "type": "uint256"
                    },
                    {
                        "indexed": False,
                        "internalType": "uint256",
                        "name": "amount1Out",
                        "type": "uint256"
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "to",
                        "type": "address"
                    }
                ],
                "name": "Swap",
                "type": "event"
            }
        ]),
        "address": "0x999fc000f3f5176306c0753bad01d6a37644feef",
        "event_name": "Swap"
    }
    monitor = EVMMonitor({
        "wallet": wallet,
        "contract": contract
    })
    monitor.transform()
    while True:
        try:
            monitor.execute()
        except:
            pass
