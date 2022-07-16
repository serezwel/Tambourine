import pymongo
from dotenv import load_dotenv
import os
import re
load_dotenv()
MONGO = os.getenv('MONGO')

client = pymongo.MongoClient(MONGO)
db = client["Tambourine"]
col = db["Bets"]

def get_bets(context=""):
    bet_list = []
    if not context:
        bets = col.find()
    else:
        bets = col.find({"context": context})
    for bet in bets:
        bet_list.append(bet)
    return bet_list

bet_list = get_bets()
str = ""
for bet in bet_list:
    str += f'Better: {bet["Better"]}\n'
    str += f'Bet: {bet["Bet"]}\n'
    str += f'Punishment: {bet["Punishment"]}\n'
    str += f'Link: {bet["Link"]}\n'
    str += '\n'
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", flags=re.UNICODE)
str = re.sub(emoji_pattern, "", str)
print(str)
f = open("bets.txt", "w+")
f.write(str)
f.close()

