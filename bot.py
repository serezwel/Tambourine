import os
import pymongo
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO = os.getenv('MONGO')
intents = discord.Intents.default()
intents.members = True

client = pymongo.MongoClient(MONGO)
db = client["Tambourine"]
col = db["Bets"]

bot = commands.Bot(command_prefix='%', description = "Hey! Hey Hey! Tambourine Club!", intents = intents)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)

@bot.command()
async def bet(ctx, bet:str, punishment:str, link:str):
    """Submit a bet
    Use quotation marks
    e.g. %bet "The mets wins the superbowl" "3 hours of rick roll" "https://youtu.be/dQw4w9WgXcQ" """
    try:
        bet_dict = {"BetID": col.count_documents({}) + 1, "Better": ctx.author.name, "Bet": bet, "Punishment": punishment, "Link": link, "Fulfilled": False}
    except Exception:
        await ctx.send("Incorrect format!")
        return
    col.insert_one(bet_dict)
    output_str = '{0.name} bets!\n'.format(ctx.author)
    output_str = output_str + f'Bet: {bet}\nPunishment: {punishment}\nLink: {link}'
    await ctx.send(output_str)

@bot.command()
async def deletebet(ctx, betID):
    """Delete a bet, use the bet ID"""
    x = col.delete_one({"BetID": betID})
    await ctx.send("Deleted bet!")

@bot.command()
async def mybets(ctx):
    """See the list of bets you made so far!"""
    x = col.find({"Better": ctx.author.name})
    output_str = ""
    for data in x:
        output_str += f'Bet ID: {data["BetID"]}\nBet: {data["Bet"]}\nPunishment: {data["Punishment"]}\nLink: {data["Link"]}\nFulfilled: {data["Fulfilled"]}\n'
        output_str += "----------------------------"
    await ctx.send(output_str)

@bot.command()
async def finishbet(ctx, betID):
    """Mark your bet finished! Use the bet ID"""
    col.update_one({"BetID": betID}, {'$set': {"Fulfilled": True}})
    await ctx.send("Bet Finished!")

bot.run(TOKEN)