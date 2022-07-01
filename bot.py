import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='%', description = "Hey! Hey Hey! Tambourine Club!", intents = intents)

@bot.command(hidden=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command(hidden=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.command(hidden=True)
async def reload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')

@bot.command(hidden=True)
@commands.is_owner()
async def shutdown(self, ctx):
    exit()


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(TOKEN)