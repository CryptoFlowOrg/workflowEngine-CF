from web3 import Web3

from handlers.web3.EventScanner import EventScanner
from models.config.properties.web3.contract import ContractConfigModel
from models.config.properties.web3.walletRead import WalletReadConfigModel
from nodes.baseNode import BaseNode
from workers.web3.EVMEventScannerProcessing import EVMEventScannerProcessing
import math
from web3.middleware import geth_poa_middleware
from time import sleep, time

from workers.workerQueue import WorkerQueue
import logging


logger = logging.getLogger(__name__)


class EVMMonitor(BaseNode):
    wallet = None
    contract = None
    sleep_duration = None
    start_block = None      # Optional
    mode = None
    events = []

    def transform(self):
        self.next_steps = self.step.get("next_steps", [])
        self.start_block = self.step.get("start_block", None)
        self.mode = self.step["mode"]
        _wallet = WalletReadConfigModel(self.step["readWallet"])
        _wallet.transform()
        if _wallet.isValid():
            self.wallet = _wallet
        _contract = ContractConfigModel(self.step["contract"])
        _contract.transform()
        if _contract.isValid():
            self.contract = _contract
        self.sleep_duration = self.step["sleep_duration"]

    def isValid(self) -> bool:
        if self.wallet is None or \
                self.contract is None or \
                self.sleep_duration is None or \
                self.mode is None:
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
            if self.start_block is not None:
                start_block = self.start_block
                self.start_block = None         # need to clear such that we do not reuse this block in future
            end_block = scanner.get_suggested_scan_end_block()
            t0 = time()
            while end_block - start_block < 10:
                sleep(5)
                start_block = state.get_last_scanned_block()
                end_block = scanner.get_suggested_scan_end_block()
            logger.debug(f"time waiting for new events {time() - t0} s")
            logger.debug(f"Scanning events from blocks {start_block} - {end_block}")
            t0 = time()
            # Run the scan
            scanner.scan(start_block, end_block, progress_callback=None)
            logger.debug(f"Completed scan from {start_block} to {end_block} in {time() - t0}s")
            state.end_chunk(end_block + 1)
            if self.mode == "ON_COMPLETE":
                self.emitEvent(self.events)
                self.events = []
            logger.debug(f"Sleeping for {self.sleep_duration}s")
            sleep(self.sleep_duration)

    def processEvent(self, tx_id: str, args: dict[str, str]):
        if self.isValidEvent(args):
            if self.mode == "ON_COMPLETE":
                self.events.append(args)
            if self.mode == "ON_RECEIVE":
                self.emitEvent(args)

    def emitEvent(self, event):
        queue = WorkerQueue.instance()
        for step in self.next_steps:
            step.update({
                "event": event
            })
            queue.newJob(step)
            logger.info(f"Event is processed and sent to step: {step['node']}")

    def isValidEvent(self, event):
        args = event["args"]
        if len(self.contract.filters) == 0:
            return True
        for filter in self.contract.filters:
            if len(filter) != len(args):
                logging.exception(f"Filter of shape {len(filter)} does not match shape of args {len(args)}")
                raise Exception("Filter shape does not match args")
            validKeys = 0
            for key in filter.keys():
                if filter[key] == "any":
                    validKeys += 1
                else:
                    if filter[key] == args[key]:
                        validKeys += 1
            if validKeys == len(filter):
                return True
        return False


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
        "readWallet": wallet,
        "contract": contract
    })
    monitor.transform()
    while True:
        try:
            monitor.execute()
        except:
            pass
