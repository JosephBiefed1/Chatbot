# Simple Telegram bot using python-telegram-bot and pandas
import logging
import pandas as pd
import re
from datetime import datetime, timedelta
from telegram import ForceReply, Update
from prediction_model import predict_crowd_level
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import string
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import io
import base64
from predictBestDaytoTravel import main as best_day_main
from predictBestHourToTravel import main as best_hour_main
load_dotenv()
import warnings
#warnings.filterwarnings("ignore", category=FutureWarning)
#warnings.filterwarnings("ignore", category=UserWarning)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

df = pd.read_csv(r'data\new_classified_messages_2.csv')
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Crowd Level'] = df['Crowd Level new'] if 'Crowd Level new' in df.columns else df['Crowd Level']
df = df[df['Crowd Level'].isin(['High', 'Low'])]

def get_latest_info(direction):
    now = datetime.now()
    #matching
    print(f'Current time: {now}')
    print(f'Current direction: {direction}')    
    #if direction.lower() != "singapore to malaysia" or direction.lower() != "malaysia to singapore":
    #   return "Invalid direction. Please use 'Singapore to Malaysia' or 'Malaysia to Singapore'."
    
    recent = df[
        (df['Direction'].str.lower() == direction.lower()) &
        (df['Date'] >= now - timedelta(minutes=30))
    ]
    if recent.empty:
        return predict_crowd_level(direction)
    
    latest = recent.sort_values('Date', ascending=False).iloc[0]
    return f"{latest['Date']}: {latest['Crowd Level']}"

def get_crowd_level_at_time(direction, query_time):
    
    print(f"Query time: {query_time}")
    print(f"Direction: {direction}")
    filtered = df[df['Direction'].str.lower() == direction.lower()]
    if filtered.empty:
        return "No data for that direction."
    filtered = filtered[~filtered['Crowd Level'].isin(['Bot message', 'Not related'])]
    if filtered.empty:
        return "No crowd level data for that direction."
    filtered = filtered.sort_values('Date')
    times = filtered['Date']
    idx_before = times.searchsorted(query_time, side='right') - 1
    idx_after = idx_before + 1
    if idx_before < 0:
        closest = filtered.iloc[0]
    elif idx_after >= len(filtered):
        closest = filtered.iloc[-1]
    else:
        before = filtered.iloc[idx_before]
        after = filtered.iloc[idx_after]
        if abs((before['Date'] - query_time).total_seconds()) <= abs((after['Date'] - query_time).total_seconds()):
            closest = before
        else:
            closest = after
    return f"{closest['Date']}: {closest['Crowd Level']}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Type 'information <direction>' for latest info within 30 min.\n"
        "Or ask: What was the crowd level on May 15 2025 at 10:00, from Singapore to Malaysia?\n"
        "Or ask: get me the best day to travel for the week\n"
        "Or ask: get me the best time to travel for Tuesday\n",
        
        reply_markup=ForceReply(selective=True),
    )
    
async def information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "This bot is a public service project created for fun and learning.\n" 
        "It predicts crowd levels at the border with about 60% accuracy—better than random guessing, but not perfect.\n"
        "The information provided is for guidance only and should not be used for commercial purposes.\n"
        "Use this bot as a helpful reference when deciding whether to travel across the border.",
        
        reply_markup=ForceReply(selective=True),
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text.strip()
    # Regex: What was the crowd level on May 15 2025 at 10:00, from Singapore to Malaysia?
    match = re.match(
        r'what was the crowd level on ([A-Za-z]+\s+\d{1,2}\s+\d{4}) at (\d{1,2}:\d{2}), from (.+)', query, re.IGNORECASE
    )
    if match:
        date_str, time_str, direction = match.groups()
        # Remove punctuation and extra whitespace from direction
        direction = direction.translate(str.maketrans('', '', string.punctuation)).strip()
        try:
            logger.info(f"Parsed date: {date_str}, time: {time_str}, direction: {direction}")
            query_time = datetime.strptime(f"{date_str} {time_str}", "%B %d %Y %H:%M")
        except Exception as e:
            logger.error(f"Error parsing date/time: {e}")
            await update.message.reply_text("Invalid time format. Please use: What was the crowd level on May 15 2025 at 10:00, from Singapore to Malaysia?")
            return
        reply = get_crowd_level_at_time(direction, query_time)
        logger.info(f"Reply: {reply}")
        await update.message.reply_text(reply)
        return

    # New: Best day to travel for the week
    if query.lower().strip() == "get me the best day to travel for the week":
        day_crowd_percent = best_day_main(df)
        # Return the DataFrame as CSV text
        csv_text = day_crowd_percent
        await update.message.reply_text(f"Crowd level percentage by day :\n{csv_text}")
        return

    # New: Best time to travel for a specific day
    match_time = re.match(r'get me the best time to travel for ([A-Za-z]+)', query, re.IGNORECASE)
    if match_time:
        day_of_week = match_time.group(1).capitalize()
        hour_crowd_percent = best_hour_main(df, day_of_week)
        csv_text = hour_crowd_percent
        await update.message.reply_text(f"Crowd level percentage by hour for {day_of_week} :\n{csv_text}")
        return

    if query.lower().startswith("information"):
        
        parts = query.split(" ", 1)
        direction = parts[1] if len(parts) > 1 else ""
        if not direction:
            logger.warning("No direction specified for information query.")
            await update.message.reply_text("Please specify a direction. Or recheck your format")
            return
        reply = get_latest_info(direction)
        logger.info(f"Information reply: {reply}")
        await update.message.reply_text(reply)
        return

    else:
        await update.message.reply_text("Please recheck your sentence structure. There might be incorrect structures that make the command invalid")
    
def main() -> None:
    print("Bot started...")
    
    application = Application.builder().token(os.environ.get('TELEGRAM_BOT_TOKEN')).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("information", information))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()