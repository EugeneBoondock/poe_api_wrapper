import os
# Install required packages
os.system("pip install discord.py python-dotenv poe-api-wrapper")
import discord
from discord.ext import commands
from poe_api_wrapper import PoeApi
import requests

# Create Discord bot instance
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize chat thread variables per Discord server
chat_threads = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Check if the bot was mentioned in the message
    if bot.user.mentioned_in(message):
        # Define the list of allowed users by their IDs
        allowed_users = [916449019541217331, 655478415377563749] # Replace these numbers with the actual IDs of eugeneboondock, glasgowmg and Earthie#8545
        
        # Check if the message author is in the list of allowed users
        if message.author.id in allowed_users:
            # Extract the description part of the message
            prompt = ' '.join(message.clean_content.split(' ')[1:])
            
            # Send the message content to the PoeApi chat bot within the existing chat thread or create a new one
            response = await ask_question(message.guild.id, "HephArt", prompt)
            # Send the response back to Discord
            await send_response(message, response) # Pass the message object instead of the channel object
        else:
            # Send a message to inform the user that they are not allowed to use the bot
            await message.channel.send(f"Sorry {message.author.mention}, ask Eugene or Glasgow to prompt me for you.")


import re # Import the regular expression module

async def ask_question(server_id, bot_name, message):
    global chat_threads
    
    # Check if there's an existing chat thread for the server
    if server_id in chat_threads:
        chat_code, chat_id = chat_threads[server_id]
    else:
        chat_code, chat_id = None, None
    
    # Send the message content to the PoeApi chat bot
    response = ""
    for chunk in poe_client.send_message(bot_name, message, chatCode=chat_code, chatId=chat_id):
        response += chunk["response"]
        
        # Check if the response contains chatCode or chatId
        if "chatCode" in chunk:
            chat_code = chunk["chatCode"]
        if "chatId" in chunk:
            chat_id = chunk["chatId"]
    
    # Update the chat thread for the server
    chat_threads[server_id] = (chat_code, chat_id)
    
    # Remove the progress text from the response
    response = response.replace("Generating image", "") # Replace the text with an empty string
    response = re.sub("\(\d+s elapsed\)", "", response) # Replace the seconds elapsed strings with an empty string using a regular expression
    
    return response

async def send_response(message, response):
    # Get the channel object from the message object
    channel = message.channel
    
    # Check if the response is an image URL
    if response.startswith("http"):
        # Download the image
        image_data = requests.get(response).content
        
        # Send the image to the channel as a reply
        await message.reply(file=discord.File(image_data, 'image.png'))
    else:
        # Send the text response
        await channel.send(response)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
