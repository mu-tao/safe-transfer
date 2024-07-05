
import json
import argparse
import bittensor as bt
from rich.prompt import Prompt, Confirm
from rich.console import Console
from bittensor.btlogging import logging as _logger

console = Console()

# First let's get the wallet from the command line.
parser = argparse.ArgumentParser('safe transfer submit')
bt.subtensor.add_args( parser )
config = bt.config( parser )

import json
from binascii import unhexlify

try:
    with open('extrinsic_output.json', 'r') as file:
        extrinsic_details = json.loads(file.read())
except Exception as e:
    print(f"[red]Error: Invalid JSON with error: {e}[/red]")