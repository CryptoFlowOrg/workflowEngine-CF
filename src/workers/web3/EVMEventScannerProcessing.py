import time
from datetime import datetime

from web3.datastructures import AttributeDict

from handlers.web3.EventScanner import EventScannerState
from typing import Callable



class EVMEventScannerProcessing(EventScannerState):
    """Process the events of scanned blocks and push to the execution queue

    It simply recognises an event and executes a call back function
    """

    def __init__(self, callback: Callable[[str, dict[str, str]], None]):
        self.state = None
        # self.fname = "wagyuswap-lp-burn-vlx-vinu.json"
        # How many second ago we saved the JSON file
        self.last_save = 0
        self.callback = callback
        self.last_scanned_block = 0

    def reset(self):
        """Create initial state of nothing scanned."""
        self.last_scanned_block = 0
        self.state = {
            "last_scanned_block": 0,
            "blocks": {},
        }

    # def restore(self):
    #     """Restore the last scan state from a file."""
    #     try:
    #         self.state = json.load(open(self.fname, "rt"))
    #         print(
    #             f"Restored the state, previously {self.state['last_scanned_block']} blocks have been scanned")
    #     except (IOError, json.decoder.JSONDecodeError):
    #         print("State starting from scratch")
    #         self.reset()
    #
    # def save(self):
    #     """Save everything we have scanned so far in a file."""
    #     with open(self.fname, "wt") as f:
    #         json.dump(self.state, f)
    #     self.last_save = time.time()

    #
    # EventScannerState methods implemented below
    #

    def get_last_scanned_block(self):
        """The number of the last block we have stored."""
        return self.last_scanned_block

    def delete_data(self, since_block):
        """Remove potentially reorganised blocks from the scan data."""
        # for block_num in range(since_block, self.get_last_scanned_block()):
        #     if block_num in self.state["blocks"]:
        #         del self.state["blocks"][block_num]

    def start_chunk(self, block_number, chunk_size):
        pass

    def end_chunk(self, block_number):
        """Save at the end of each block, so we can resume in the case of a crash or CTRL+C"""
        # Next time the scanner is started we will resume from this block
        self.last_scanned_block = block_number

        # Save the database file for every minute
        # if time.time() - self.last_save > 60:
        #     self.save()

    def process_event(self, block_when: datetime, event: AttributeDict) -> str:
        # Events are keyed by their transaction hash and log index
        # One transaction may contain multiple events
        # and each one of those gets their own log index

        # event_name = event.event # "Transfer"
        log_index = event.logIndex  # Log index within the block
        txhash = event.transactionHash.hex()  # Transaction hash
        block_number = event.blockNumber
        tx_id = f"{block_number}-{txhash}-{log_index}"

        # Convert ERC-20 Transfer event to our internal format
        args = event["args"]
        self.callback(tx_id, args)

        # Return a pointer that allows us to look up this event later if needed
        return tx_id
