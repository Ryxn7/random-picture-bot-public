import os
import discord
from discord.ext import commands
from loguru import logger
import json


with open("data/database.json", "r") as f:
    data = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
token = data["token"]
client = commands.Bot(command_prefix='b.', case_insensitive=True, intents=intents)
client.remove_command('help')


def loadCogs():
   for file in os.listdir("cogs"):
       if file.endswith(".py"):
           name = file[:-3]
           client.load_extension(f"cogs.{name}")
           logger.info(f"Loaded cogs.{name}")

loadCogs()

client.run(token)