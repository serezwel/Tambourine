import os
import pymongo
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import date

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO = os.getenv('MONGO')
intents = discord.Intents.default()
intents.members = True
try:    
    client = pymongo.MongoClient(MONGO)
    db = client["Tambourine"]
    col = db["Bets"]
except Exception as e:
    print("Failed", e)
    quit()

bot = commands.Bot(command_prefix='%', description = "Hey! Hey Hey! Tambourine Club!", intents = intents)
def next_sequence_value(sequence_name):
    sequence_doc = db["Counter"].find_one_and_update({"_id":sequence_name}, {"$inc": {"sequence_value": 1}})
    return sequence_doc["sequence_value"]
def create_embed(author, output_list, page_num):
    embed = discord.Embed(title=author, description = "Here are your bets!",color=discord.Colour.from_rgb(255, 255, 51))
    embed.add_field(name="Bet ID", value = output_list[page_num]["BetID"], inline=False)
    embed.add_field(name="Bet", value = output_list[page_num]["Bet"], inline=False)
    embed.add_field(name="Punishment", value = output_list[page_num]["Punishment"], inline=False)
    embed.add_field(name="Link", value = output_list[page_num]["Link"], inline=False)
    embed.add_field(name="Status", value = output_list[page_num]["Status"], inline=False)
    embed.add_field(name="Page", value=page_num + 1, inline=False)
    
    return embed
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
        bet_dict = {"BetID": next_sequence_value("betid") + 1, "Better": ctx.author.name, "Bet": bet, "Punishment": punishment, "Link": link, "Status": "Pending"}
    except Exception as e:
        print(e)
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
async def mybets(ctx, page_num = 0):
    """See the list of bets you made so far!"""
    x = col.find({"Better": ctx.author.name})
    output_list = []
    for data in x:
        output_list.append(data) 
    if len(output_list) == 0:
        await ctx.send("You have no bets!")
        return
    embed = create_embed(ctx.author.name, output_list, page_num)
    msg = await ctx.send(embed=embed)
    next_emoji = '➡️'
    prev_emoji = '⬅️'
    await msg.add_reaction(prev_emoji)
    await msg.add_reaction(next_emoji)


@bot.command()
async def finishbet(ctx, betID, result):
    """Mark your bet finished! Use the bet ID"""
    if result == "W".lower():
        col.update_one({"BetID": int(betID)}, {'$set': {"Status": "Won"}})
    elif result == "L".lower():
        col.update_one({"BetID": int(betID)}, {'$set': {"Status": "Lost"}})

@bot.command()
async def changebet(ctx, betID, bet_param, new_param):
    """Specify your bet ID along with the bet parameter you wish to change and the change you want to make!
    Parameter options: Bet (what you are betting), Punishment (the punishment if you lose your bet), Link (link to the x hours video)"""
    col.update_one({"BetID": int(betID)}, {'$set': {bet_param: new_param}})
    await ctx.send("Successfully changed!")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    page_num = int(msg.embeds[0].fields[-1].value)
    if payload.emoji == '➡️':
        page_num += 1
    if payload.emoji == '⬅️':
        page_num -= 1
    x = col.find({"Better": msg.embeds[0].title})
    output_list = []
    for data in x:
        output_list.append(data)
    if page_num < 0:
        page_num = len(output_list) - 1
    elif page_num >= len(output_list):
        page_num = 0
    embed = create_embed(msg.embeds[0].title, output_list, page_num)
    await msg.edit(embed=embed)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return
    msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    page_num = int(msg.embeds[0].fields[-1].value)
    if payload.emoji == '➡️':
        page_num += 1
    if payload.emoji == '⬅️':
        page_num -= 1
    x = col.find({"Better": msg.embeds[0].title})
    output_list = []
    for data in x:
        output_list.append(data)
    if page_num < 0:
        page_num = len(output_list) - 1
    elif page_num >= len(output_list):
        page_num = 0
    embed = create_embed(msg.embeds[0].title, output_list, page_num)
    await msg.edit(embed=embed)

bot.run(TOKEN)