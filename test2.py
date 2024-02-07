import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from poe_api_wrapper import PoeApi
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv("config.env")

# Load API tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Poe API client
poe_client = None

# Create Discord bot instance
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize chat thread variables
chat_code = None
chat_id = None

@bot.event
async def on_ready():
    global poe_client
    logging.info(f'Logged in as {bot.user.name}')
    try:
        poe_client = PoeApi("E8cpZIkCqbj2TO6p1uaP-Q==")
    except Exception as e:
        logging.error(f"Failed to initialize PoeApi client: {e}")

@bot.event
async def on_message(message):
    # Check if the message author is the bot itself
    if message.author == bot.user:
        return
    
    # Check if the bot was mentioned in the message
    if bot.user.mentioned_in(message):
        # Send the message to the PoeApi chat bot within the existing chat thread
        response = await ask_question("Earthie", message.content)
        # Send the response back to Discord
        await message.channel.send(response)

async def ask_question(bot, message):
    global chat_code, chat_id
    
    # Check if PoeApi client is initialized
    if poe_client is None:
        logging.warning("PoeApi client is not initialized. Skipping message processing.")
        return ""

    # Send message to an existing chat thread if chat_code or chat_id is provided
    chat_param = {}
    if chat_code:
        chat_param["chatCode"] = chat_code
    elif chat_id:
        chat_param["chatId"] = chat_id
    
    # Retry logic with exponential backoff
    retries = 3  # Number of retries
    delay = 1    # Initial delay in seconds
    for attempt in range(retries):
        try:
            response = ""
            for chunk in poe_client.send_message(bot, message, **chat_param):
                response += chunk["response"]
                # Check if the response contains chatCode or chatId
                if "chatCode" in chunk:
                    chat_code = chunk["chatCode"]
                if "chatId" in chunk:
                    chat_id = chunk["chatId"]
            return response
        except RuntimeError as e:
            # Handle specific error related to rate-limiting
            if "Rate limit exceeded" in str(e):
                logging.warning(f"Rate limit exceeded. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            else:
                # Handle other runtime errors
                logging.error(f"Error occurred: {e}")
                raise
    # If all retries fail, raise an exception
    raise RuntimeError("Failed to send message after multiple retries")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
