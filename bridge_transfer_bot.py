import os
import json
import discord
from discord.ext import commands
import logging
from binascii import unhexlify
import bittensor as bt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a dictionary to act as a simple persistent database
database = {}

# Load the database from a file if it exists
def load_database():
    if os.path.exists('database.json'):
        with open('database.json', 'r') as db_file:
            return json.load(db_file)
    return {}

# Save the database to a file
def save_database():
    with open('database.json', 'w') as db_file:
        json.dump(database, db_file, indent=4)

# Verify the transaction data
def verify_transaction(transaction_data):
    try:
        keypair = bt.Keypair(transaction_data['coldkey_ss58'])
        if not keypair.verify(transaction_data['extrinsic_data'], unhexlify(transaction_data['signature'].encode())):
            return False, 'Signature verification failed.'
        return True, None
    except Exception as e:
        return False, f'Error during verification: {e}'
    
    
async def handle_help(message):
    help_message = (
        "# Help Menu\n"
        "Here are the commands you can use:\n"
        "1. **/help** - Show this help message\n"
        "2. **/list** - Show a list of your extrinsics one per coldkey with corresponding extrinsic snippets.\n"
        "3. **Send a DM** with a transaction file attached to update the database.\n"
    )
    # await message.channel.send(f"```markdown\n{help_message}\n```")
    await message.channel.send(help_message)
    logger.info('Help message sent.')
    
async def handle_list(message):
    user_discriminator = str(message.author.discriminator)
    if user_discriminator not in database:
        await message.channel.send('No transaction data found for your username')
        logger.info('No transaction data found for user.')
        return
    else:
        user_transactions = database[user_discriminator]
        if isinstance(user_transactions, list):
            table_header = "| Coldkey SS58                                     | Transfer Data |\n|--------------------------------------------------|---------------|\n"
            extrinsic_data_list = [f"| {data['coldkey_ss58']:<44} | {data['extrinsic_data'][:5]}...{data['extrinsic_data'][-5:]} |" for data in user_transactions]
            pretty_extrinsic_data = '\n'.join(extrinsic_data_list)
            await message.channel.send(f'Your extrinsic_data:\n```markdown\n{table_header}{pretty_extrinsic_data}\n```')
            logger.info('Extrinsic data shown.')
        else:
            await message.channel.send('Error: Invalid data format for your transactions.')
            logger.error('Invalid data format for user transactions.')
        
async def handle_transaction_file(message):
    
    # Get user metadata.
    user_name = str(message.author)
    user_id = str(message.author.id)
    user_discriminator = str(message.author.discriminator)
    user_display_name = str(message.author.display_name)
    message_id = str(message.id)
    message_timestamp = str(message.created_at.isoformat())
    attachment = message.attachments[0]
    
    # Download and load the tmp file.
    os.makedirs('transactions', exist_ok=True)    
    tmp_file_path = f'transactions/tmp.json'
    await attachment.save(tmp_file_path)
    logger.info(f'Saved tmp file to {tmp_file_path}')
    with open(tmp_file_path, 'r') as file:
        new_transaction_data = json.loads(file.read())
        
    # Add additional info to the transaction.
    new_transaction_data.update({
        'user_name': user_name,
        'user_id': user_id,
        'user_discriminator': user_discriminator,
        'user_display_name': user_display_name,
        'message_id': message_id,
        'message_timestamp': message_timestamp
    })
    logger.info(f'New transaction data: {new_transaction_data}')

    # Perform verification on the new transaction.
    is_valid, error_message = verify_transaction(new_transaction_data)
    if not is_valid:
        await message.channel.send(f'Error: {error_message}')
        logger.error(error_message)
        return
    
    # Check for duplicate coldkey_ss58 address for the same user and remove it
    user_transactions = database.get(user_discriminator, [])
    # Remove older transaction with previous coldkey.
    user_transactions = [old_transaction for old_transaction in user_transactions if old_transaction['coldkey_ss58'] != new_transaction_data['coldkey_ss58']]
    
    # Check for duplicate coldkey_ss58 address for different users
    for other_user_discriminator, other_user_transactions in database.items():
        if other_user_discriminator != user_discriminator:  # Ensure we are not checking the same user
            for other_old_transaction in other_user_transactions:
                if other_old_transaction['coldkey_ss58'] == new_transaction_data['coldkey_ss58']:
                    await message.channel.send('Error: A different user has already submitted a transaction with the same coldkey_ss58 address. We need to arbitrate this transaction.')
                    logger.warning('Duplicate coldkey_ss58 address found for different users.')
                    return
            
    # Add the transaction to the user's list of transactions
    user_transactions.append(new_transaction_data)
    database[ user_discriminator ] = user_transactions
    save_database()
    logger.info('Database updated.')
    extrinsic = new_transaction_data.get('extrinsic', '')
    extrinsic_details = f"{extrinsic[:5]}...{extrinsic[-5:]}"
    await message.channel.send(f'Transaction file received, verified, and updated. Coldkey: {new_transaction_data["coldkey_ss58"]}, Extrinsic: {extrinsic_details}')

# Handle incoming messages
async def handle_message(message):
    if message.content == '/help':
        await handle_help(message)
    elif message.content == '/list':
        await handle_list(message)
    elif isinstance(message.channel, discord.DMChannel) and message.attachments:
        await handle_transaction_file(message)
    else:
        await bot.process_commands(message)

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.dm_messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    logger.info(message)
    await handle_message(message)

# Load the database
database = load_database()
logger.info('Database loaded.')

# Run the bot with your token
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
logger.info('Bot started.')

