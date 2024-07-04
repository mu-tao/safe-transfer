# The MIT License (MIT)
# Copyright © 2024 Opentensor Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# A simply script to figure out if the details passed are properly formatted and signed.
import json
from binascii import unhexlify

with open('sample.txt', 'r') as file:
    thing = file.read()
try:
    extrinsic_details = json.loads(thing)
except Exception as e:
    print(f"[red]Error: Invalid JSON with error: {e}[/red]")
 
import bittensor as bt  
for user, el in extrinsic_details.items(): 
    keypair = bt.Keypair(el['extrinsic_data'])
    print(
        user, keypair.verify( el['extrinsic_data'].encode(), unhexlify( el['signature'].encode()))
    )
    
    