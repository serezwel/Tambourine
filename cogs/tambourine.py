import discord
from discord.ext import commands
import pymongo
from dotenv import load_dotenv
import os
os.chdir('../')
MONGO = os.getenv('MONGO')
try:    
    client = pymongo.MongoClient(MONGO)
    db = client["Tambourine"]
    col = db["Bets"]
except Exception as e:
    print("Failed", e)
    quit()

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

class Tambourine(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tambourine Bot is Live!")

    @commands.command()
    async def bet(self, ctx, bet:str, punishment:str, link:str="None"):
        """Submit a bet
        Use quotation marks
        e.g. %bet "The mets wins the superbowl" "3 hours of rick roll" "https://youtu.be/dQw4w9WgXcQ"
        For no link bets,  Please do NOT include the third input!
        e.g. %bet "The mets wins the superbowl" "I will cosplay as nagNose" """
        if not link:
            await ctx.send("Please include the link! If it's a non-video bet, use the no link format!")
            return
        try:
            bet_dict = {"BetID": next_sequence_value("betid") + 1, "Better": ctx.author.name, "Bet": bet, "Punishment": punishment, "Link": link, "Status": "Pending"}
        except Exception as e:
            print(e)
            return
        col.insert_one(bet_dict)
        output_str = '{0.name} bets!\n'.format(ctx.author)
        output_str = output_str + f'Bet: {bet}\nPunishment: {punishment}\nLink: {link}'
        await ctx.send(output_str)

    @commands.command()
    async def deletebet(self, ctx, betID):
        """Delete a bet, use the bet ID"""
        x = col.delete_one({"BetID": int(betID)})
        await ctx.send("Deleted bet!")

    @commands.command()
    async def mybets(self, ctx, page_num = 0):
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


    @commands.command()
    async def finishbet(self, ctx, betID, result):
        """Mark your bet finished! Use the bet ID. Result: L for Loss, W for Win (e.g. %finishbet 1 L)"""
        if result == "W".lower():
            col.update_one({"BetID": int(betID)}, {'$set': {"Status": "Won"}})
        elif result == "L".lower():
            col.update_one({"BetID": int(betID)}, {'$set': {"Status": "Lost"}})

    @commands.command()
    async def changebet(self, ctx, betID, bet_param, new_param):
        """Specify your bet ID along with the bet parameter you wish to change and the change you want to make!
        Parameter options: Bet (what you are betting), Punishment (the punishment if you lose your bet), Link (link to the x hours video)"""
        col.update_one({"BetID": int(betID)}, {'$set': {bet_param: new_param}})
        await ctx.send("Successfully changed!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return
        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
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

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.client.user.id:
            return
        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
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
def setup(client):
    client.add_cog(Tambourine(client))