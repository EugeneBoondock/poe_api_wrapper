import discord
from dotenv import load_dotenv
import os
from poe_api_wrapper import PoeApi

# Load environment variables from .env file
load_dotenv("config.env")

# Load API tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Poe API client
poe_client = PoeApi("HJ-av6eUsk2llTMCBj5cKg==")

# Create Discord client
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    # Check if the bot was mentioned in the message
    if client.user.mentioned_in(message):
        # Create a new chat thread with the specified message
        response = await create_chat_thread("a2", message.content)
        # Print the response
        print(response)

async def create_chat_thread(bot, message):
    # Streamed example
    for chunk in poe_client.send_message(bot, message):
        print(chunk["response"], end="", flush=True)
    print("\n")

    # Non-streamed example
    chunk = None
    for chunk in poe_client.send_message(bot, message):
        pass
    print(chunk["text"])

    # Get chatCode, chatId, and title
    chatCode = chunk["chatCode"]
    chatId = chunk["chatId"]
    title = chunk["title"]

    # Send message to an existing chat thread
    # 1. Using chatCode
    for chunk in poe_client.send_message(bot, message, chatCode=chatCode):
        print(chunk["response"], end="", flush=True)
    # 2. Using chatId
    for chunk in poe_client.send_message(bot, message, chatId=chatId):
        print(chunk["response"], end="", flush=True)

# Run the client
client.run(DISCORD_TOKEN)
