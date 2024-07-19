import discord
from discord.ext import commands
import os
from functools import wraps
import asyncio
import matplotlib.pyplot as plt
from utils import delete_user_msg_after, delete_bot_msg_after
from poll import setup_poll_commands

# get the token from the .env file
TOKEN = os.environ['DISCORD_TOKEN']

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# The bot will listen for commands that start with the prefix '!'
bot = commands.Bot(command_prefix='!', intents=intents)

# Store poll data
poll_data = {}

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command()
@delete_user_msg_after(5)
@delete_bot_msg_after(5)
async def ping(ctx):
    return await ctx.send('Pong!')

@bot.command()
@delete_user_msg_after(5)
@delete_bot_msg_after(5)
async def hello(ctx):
    return await ctx.send(f'Hello, {ctx.author.name}!')
    
# Load poll commands
setup_poll_commands(bot)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        response = await ctx.send('Please provide all required arguments.')
    elif isinstance(error, commands.BadArgument):
        response = await ctx.send('Please provide valid arguments.')
    else:
        response = await ctx.send('An error occurred.')
    await asyncio.sleep(10)
    await ctx.message.delete()
    await asyncio.sleep(10)
    await response.delete()

bot.run(TOKEN)
