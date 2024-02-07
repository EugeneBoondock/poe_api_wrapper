import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from poe_api_wrapper import PoeApi

# Load environment variables from .env file
load_dotenv("config.env")

# Load API tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Poe API client
poe_client = PoeApi('HJ-av6eUsk2llTMCBj5cKg==')

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
    print(f'Logged in as {bot.user.name}')

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
    
    # Send message to an existing chat thread if chat_code or chat_id is provided
    chat_param = {}
    if chat_code:
        chat_param["chatCode"] = chat_code
    elif chat_id:
        chat_param["chatId"] = chat_id
    
    # Send the message to the PoeApi chat bot
    response = ""
    for chunk in poe_client.send_message(bot, message, **chat_param):
        response += chunk["response"]
        
        # Check if the response contains chatCode or chatId
        if "chatCode" in chunk:
            chat_code = chunk["chatCode"]
        if "chatId" in chunk:
            chat_id = chunk["chatId"]
    
    return response

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
