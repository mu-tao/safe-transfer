
# Safe Transfer

On July 2nd 2024 the Bittensor network experienced hacks on a number of wallets. In reaction to the abrupt and large scale attack the Opentensor Foundation decided to firewall the chain ('make the chain un-accessible to further transactions') until the attack could be contained. In the following day we discovered that the root cause of the attack came from a compromised 6.12.2 version which was latest on PyPy from May 22nd until May 29th 2024 and which leaked wallet mnemonic details to the attacker when users called some wallet functions. It is possible that a large number of wallets that were actively using the Bittensor CLI at that time were compromised by the attack.

This repository is designed to help those users by creating a `safe_transfer` transaction -- a legitimately signed transfer transaction from their potentially compromised wallet -- which will be hand carried across the chain firewall and allowed to execute on the Bittensor Finney network. However, some of the wallets making these transactions could be compromised themselves, and therefore the attacker could create legitimate transactions which we could not discern. To mitigate this risk OTF will perform the following process to filter and arbitrate between malicious transactions and those submitted by their previous owners. 

> Note, this is simply our best effort, for some cases it might be impossible to arbitrate between legitimate transactions from previous owners and the attacker.
> However, we highly suspect that people affected by this attack were common participants of the Bittensor discord and that we will be able to identify them individually.

1. Users of this script will use the `python safe_transfer.py` function to create a text-based transaction printed on their terminal. 
2. The users will then message the ligitmately signed transaction to a verified member of the Bittensor discord with username 'safe_transfer_helper' within the channel 'safe_transfer' channel.
3. All safe transfers will be collected during a period of X days and will be filtered as follows.
    3.1 If the transaction is not legitimately signed the transaction will be removed.
    3.2 If the transaction is signed but there are multiple transactions from the same wallet we will arbitrate which transaction is has precendence based on the 
    time the discord user has been active in the Bittensor discord. However, if the user participates in more than 1 arbitrated transaction, neither of their transactions will be included.
    3.3 If both during an arbitration are new to the Bittensor discord from within the week, and are not participating in the multiple arbitrations then we will discard both transactions. 

# How to create a safe transfer?

1. First, git clone this repository on to the device which contains the wallet with the coldkey you suspect is compromised.
```bash
git clone git@github.com:opentensor/safe-transfer.git
```

2. Second, install the requirements for this repository which simply includes the safe `bittensor>=7.0.0` requirement and `rich` for terminal output colouring.
```bash
cd safe-transfer; python -m pip install -r requirments.txt
```

3. Third, run the `safe_transfer.py` script, passing your old_wallet name and the address to the wallet you want to transfer funds to ss58_encoded.
> Note: 
> 1. this must be run on the machine with the old_wallet who's key is potentially compromised.
> 2. The safe_transfer script does NOT execute this command it simply creates it and prints it to the screen.
> 3. Make sure that YOU own the other wallet who's address you pass to the script. For instance, check for this value on the Bittensor wallet extension.
> Or run $ btcli w list to see the addresses of other wallet's available for the transfer.
```bash
python safe_transfer.py --old_wallet=<the name of your old wallet> --new_wallet_address=<the ss58_address to the new wallet>

# For example:
        python safe_transfer.py --old_wallet=my_wallet_name --new_wallet_address=5DPB62QK6XsSbuFd9g4QAzqq9P5Pzi32P2wBSRS4jdJGLcew
```

