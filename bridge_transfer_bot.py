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
        if not keypair.verify(transaction_data['extrinsic_data'].encode(), unhexlify(transaction_data['signature'].encode())):
            return False, 'Signature verification failed.'
        return True, None
    except Exception as e:
        return False, f'Error during verification: {e}'

# Handle incoming messages
async def handle_message(message):
    if isinstance(message.channel, discord.DMChannel) and message.attachments:
        user_name = str(message.author)
        attachment = message.attachments[0]
        
        # Ensure the transactions directory exists
        os.makedirs('transactions', exist_ok=True)
        
        # Download the file
        file_path = f'transactions/{user_name}.json'
        await attachment.save(file_path)
        logger.info(f'File saved to {file_path}')
        
        # Read the file content
        try:
            with open(file_path, 'r') as file:
                transaction_data = json.loads(file.read())
        except Exception as e:
            await message.channel.send(f'Error: Invalid JSON with error: {e}')
            logger.error(f'Invalid JSON with error: {e}')
            return
        
        # Perform verification
        is_valid, error_message = verify_transaction(transaction_data)
        if not is_valid:
            await message.channel.send(f'Error: {error_message}')
            logger.error(error_message)
            return
        
        # Check for duplicate coldkey_ss58 address
        for user, data in database.items():
            if data['coldkey_ss58'] == transaction_data['coldkey_ss58'] and user != user_name:
                await message.channel.send('Error: A different user has already submitted a transaction with the same coldkey_ss58 address. We need to arbitrate this transaction.')
                logger.warning('Duplicate coldkey_ss58 address found.')
                return
        
        # Check if the file is replacing an existing entry
        if user_name in database:
            await message.channel.send('Replacing existing transaction file.')
            logger.info('Replacing existing transaction file.')
        else:
            await message.channel.send('New transaction file received.')
            logger.info('New transaction file received.')
        
        # Update the database
        database[user_name] = transaction_data
        save_database()
        logger.info('Database updated.')
        
        await message.channel.send('Transaction file received, verified, and updated.')
    elif message.content == '/help':
        help_message = (
            "Here are the commands you can use:\n"
            "/help - Show this help message\n"
            "/show - Show the extrinsic_data of your transactions\n"
            "Send a DM with a transaction file attached to update the database."
        )
        await message.channel.send(help_message)
        logger.info('Help message sent.')
    elif message.content == '/show':
        user_name = str(message.author)
        if user_name in database:
            extrinsic_data = database[user_name]['extrinsic_data']
            await message.channel.send(f'Your extrinsic_data: {extrinsic_data}')
            logger.info('Extrinsic data shown.')
        else:
            await message.channel.send('No transaction data found for your user.')
            logger.info('No transaction data found for user.')
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

