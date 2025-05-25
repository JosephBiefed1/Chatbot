from telethon import TelegramClient
from datetime import datetime, timezone
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os
import asyncio
import nest_asyncio
import pytz  # Import pytz for timezone handling
import pandas as pd
load_dotenv()

# Apply the nest_asyncio patch to allow nested event loops
nest_asyncio.apply()

# Use your own values from my.telegram.org
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
session_string = os.getenv('SESSION_STRING')

# Create the client with the saved session string
client = TelegramClient(StringSession(session_string), api_id, api_hash)

def merge_replies(row, df):
    if row['Reply_to'] != -1:
        # Find the main message by 'ID' of the row's 'Reply_to'
        main_message = df[df['ID'] == row['Reply_to']]['Message'].values
        if main_message.size > 0:
            # Ensure both main_message[0] and row['Message'] are strings and not None
            main_msg = main_message[0] if main_message[0] is not None else ''
            reply_msg = row['Message'] if row['Message'] is not None else ''
            return main_msg + " " + reply_msg
    # Also ensure row['Message'] is not None
    return row['Message'] if row['Message'] is not None else ''

async def fetch_messages(count=20):
    await client.start(phone_number)

    # Getting information about yourself
    me = await client.get_me()

    username = me.username
    output = []
    async for message in client.iter_messages(-1001957076600):
        #print(message)
        output.append(message)
        if len(output) > count:
            break

    return output

def merge_replies_df(output):
    data = {}
    data['Date'] = list(map(lambda x: x.date.astimezone(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'), output))
    data['Message'] = list(map(lambda x: x.message, output))
    data['ID'] = list(map(lambda x: x.id, output))
    data["Reply_to"] = list(map(lambda x: -1 if not x.reply_to else x.reply_to.reply_to_msg_id, output))
    df = pd.DataFrame(data)
    # Apply the merge function to each row
    df['Merged_Message'] = df.apply(lambda row: merge_replies(row, df), axis=1)

    return df


async def main():
    output = await fetch_messages(10) # Adjust the count as needed
    
    
    """
    5 days -> 500, 
    1 month -> 3000.
    1 year -> 36500.
    """
    
    df = merge_replies_df(output)

    df.to_csv('data/telegram_messages.csv', index=False)
    
if __name__ == '__main__':
    asyncio.run(main())

