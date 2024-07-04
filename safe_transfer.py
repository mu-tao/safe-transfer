import json
import argparse
import bittensor as bt
from rich.prompt import Prompt, Confirm
from rich.console import Console
from bittensor.btlogging import logging as _logger

console = Console()

# First let's get the wallet from the command line.
parser = argparse.ArgumentParser('safe transfer command')
parser.add_argument('--old_wallet', type=str, help='The name of the wallet which you want to transfer from.', default=None)
parser.add_argument('--new_wallet_address', type=str, help='The addres of the wallet you want to transfer funds to.', default=None)
bt.wallet.add_args( parser )
config = bt.config( parser )

# First check that we can reach the chain.
_logger.off()
try:
    sub = bt.subtensor()
except Exception as e:
    console.print(f"[bold white]\n\tYou, failed to connect to the chain over internet. Please check your internet connection and retry:[/bold white] [red]\n\t{e}[/red]")
    exit()

# Let's check the wallet name
# Get the wallet name from the config or prompt the user
old_wallet_name = config.old_wallet
if not config.is_set('old_wallet'):
    console.print("[bold white]You must specify the [blue] \"--old_wallet\" [/blue] command line argument. [/bold white]")
    console.print("[white]\n\t> The [blue]\"--old_wallet\"[/blue] is the wallet that will transfer the funds to the new [red]\"--new_wallet_address\"[\red] [/white]")
    console.print("[white]\t> Run the command like this:[/white]")
    console.print("[white]\t\t$ python3 safe_transfer.py --old_wallet=[blue]<old_wallet_name>[/blue] --new_wallet_address=[red]<new_wallet_address>[/red][/white]")
    console.print("[white]\t> For example:[/white]")
    console.print("[white]\t\t$ python3 safe_transfer.py --old_wallet=[blue]my_OLD_fav_wallet[/blue] --new_wallet_address=[red]5DPB62QK6XsSbuFd9g4QAzqq9P5Pzi32P2wBSRS4jdJGLcew[/red]\t[/white]")
    console.print("[red]Aborting\n[/red]")
    exit()
    
# Lets get the new wallet name
new_wallet_address = config.new_wallet_address
if not config.is_set('new_wallet_address'):
    console.print("[bold white]\nYou must specify the [red]\"--new_wallet_address\"[/red] command line argument.[/bold white]")
    console.print("[white]\n\t> The [red]\"--new_wallet_address\"[/red]is the address that will receive the funds transfered from the [blue]\"--old_wallet\"[/blue][/white]")
    console.print("[white]\t> Run the command like this:[/white]")
    console.print("[white]\t\t$ python3 safe_transfer.py --old_wallet=[blue]<old_wallet_name>[/blue] --new_wallet_address=[red]<new_wallet_name>[/red][/white]")
    console.print("[white]\t> For example:[/white]")
    console.print("[white]\t\t$ python3 safe_transfer.py --old_wallet=[blue]my_fav_wallet[/blue]  --new_wallet_address=[red]5DPB62QK6XsSbuFd9g4QAzqq9P5Pzi32P2wBSRS4jdJGLcew[/red][/white]")
    console.print("[red]Aborting\n[/red]")
    exit()
    
# Create a wallet object with the specified name
old_wallet = bt.wallet(name=old_wallet_name)

# Assert that the old wallet exists.
if not old_wallet.coldkey_file.is_readable():
    console.print(f"[bold white]\nThe wallet [blue]\"{old_wallet_name}\"[/blue] does not exist on this device.[/bold white]")
    console.print(f"[white]\n\t> You must run this command from the device where this wallet is stored.[/white]")
    console.print(f"[white]\t> To see which wallets are stored on this device run the following command on your terminal:[/white]")
    console.print("[white]\t\t$ btcli wallet list[/white]")
    console.print("[white]\t\t> or[/white]")
    console.print("[white]\t\t$ ~/.bittensor/wallets\n[/white]")
    console.print("[red]Aborting\n[/red]")
    exit()
    

# Assert that the new wallet exist.
# if not new_wallet.coldkey_file.is_readable():
#     console.print(f"[bold white]\nThe wallet [red]\"{new_wallet_name}\"[/red] does not exist on this device.[/bold white]")
#     console.print(f"[white]\n\t> You must create [red]\"{new_wallet_name}\"[/red] before running this command. [/white]")
#     console.print(f"[white]\t> To create [red]\"{new_wallet_name}\"[/red] on this device run the following command from your terminal:[/white]")
#     console.print(f"[white]\t\t$ btcli wallet create --wallet.name=[red]{new_wallet_name}[/red]\n[/white]")
#     console.print("[red]Aborting\n[/red]")
#     exit()
    
# Print wallet information
# console.print("-" * 50)
# console.print("\n[bold white]===== Transaction =====[/bold white]")
# console.print(f"  [bold white]\n\t> Old Wallet Name:[/bold white] [blue]{old_wallet_name}[/blue] \n\t\t> [white]address: {old_wallet.coldkeypub.ss58_address}[/white]")
# console.print(f"  [bold white]\n\t> New Wallet Address: [red]{new_wallet_address}[/red][/bold white]")
# console.print(f"[bold white]\n> NOTE: this only CREATES the transaction and [yellow]prints[/yellow] it to the screen. It does NOT send the transaction to the chain.[/bold white]")
# console.print(f"[bold white]\n> [yellow]WARNING[/yellow]: Make sure that the address: [red]{new_wallet_address}[/red] corresponds correctly to the wallet where you want to transfer the funds. If this is not the correct wallet abort with ctrl-c.")
# if not Confirm.ask(f"[bold white]\nWould you like to sign the above transaction with your [blue]\"{old_wallet_name}\"[/blue] wallet and CONTINUE?[/bold white]\n"):
#     console.print("[red]Exiting[/red]")
#     exit()


# Decrypt and continue.
console.print(f"[bold white]\nUnlock your [blue]{old_wallet_name}[/blue] wallet to [yellow]print[/yellow] the safe transfer transaction to screen: [red]{new_wallet_address}[/red]\n[/bold white]")
old_wallet.coldkey

# Create the swap command.
console.print("\n[bold white]Printing the safe transfer to screen...[/bold white]")
try:
        call = sub.substrate.compose_call(
            call_module="Balances",
            call_function="transfer_allow_death",
            call_params={
                "dest": new_wallet_address,
                "value": 0
            },
        )

        extrinsic = sub.substrate.create_signed_extrinsic(
            call = call, 
            keypair = old_wallet.coldkey
        )
except Exception as e:
    console.print(f"[bold red]An error occured while creating the transfer transaction: {e}[/bold red]")
    console.print(f"[bold red]Please reach out to moderators in the Bittensor discord with your error.[/bold red]")
    exit()


console.print("\n[bold white]===== Transfer Details =====[/bold white]")
console.print("-" * 50)
console.print(f"[bold cyan]\t> Old Wallet Name:[/bold cyan] [blue]{old_wallet_name}[/blue] \n\t\t> [blue]address: {old_wallet.coldkeypub.ss58_address}[/blue]")
console.print(f"[bold cyan]\t> New Wallet Address: [red]{new_wallet_address}[/red][/bold cyan]")
console.print("-" * 50)
console.print("[bold white]===== End of Transfer Details =====[/bold white]\n")

# Print the extrinsic nicely on the screen
console.print("\n[bold white]===== Safe Transfer Transaction =====[/bold white]")
console.print("-" * 50)
console.print(f"[yellow]{extrinsic.__str__().replace(chr(10), ' ')}[/yellow]")
console.print("-" * 50)
console.print("[bold white]===== End of Safe Transfer Transaction Details =====[/bold white]\n")

# Print instructions to the user
console.print("\n[bold green]===== Instructions =====[/bold green]")
console.print("\n[bold white]Instructions for completing the wallet safe transfer:[/bold white]")
console.print(f"""
[bold green][1].[/bold green] First review all of the items in [cyan]transfer details[/cyan] (above) to make sure you are transfering to and from the correct keys. You must make sure you have access to the wallet with address: [red]\"{new_wallet_address}\"[/red] specified, that it\'s mnemonic is stored safely, and you have the password available to decrypt the file. Otherwise you may not be able to access the funds after they have been transfered to the new address.

[bold green][2].[/bold green] Second, COPY the above text that is in [yellow]yellow[/yellow] (above). Make sure to copy the entire contents that appear as [yellow]yellow[/yellow] on your screen.

[bold green][3].[/bold green] Next join or enter the Bittensor Discord server by following this link: https://discord.gg/bittensor.

[bold green][4].[/bold green] Once you have joined the server navigate to the ⛑・safe_transfer channel on the discord. Look for the member with a [purple]purple[/purple] username and username [purple]\"safe_transfer\"[/purple]. Click on their [purple]username[/purple] and send them a direct message. Paste the [yellow]yellow[/yellow] details into this direct message. Do NOT leave the Bittensor Discord after you do this.

[bold green][5].[/bold green] From here, this verified user will copy this transaction and pass it to the chain (which is currently firewalled). Note, we cannot edit any of the details of this transaction. The chain itself will verify its legitimacy as a normal transaction. The user is merely shuttling the transaction through to the chain.
""")

console.print("\n[bold white]Please follow the above [bold green]instructions[/bold green] carefully to complete the safe transfer process.[/bold white]\n")


