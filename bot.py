import os
import json
import logging
import datetime
import telegram
from telegram.ext import Updater, CommandHandler
from googleapiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler

# Telegram Bot Token (Replace with your actual token)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Google Calendar API Setup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Authenticate and get credentials
flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=8080)

service = build("calendar", "v3", credentials=creds)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Setup
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Function to Fetch Upcoming Events
def get_upcoming_events():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(calendarId="primary", timeMin=now, maxResults=5, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])
    return events

# Function to Send Reminder
def send_reminder(event):
    event_name = event["summary"]
    start_time = event["start"]["dateTime"]
    start_time = datetime.datetime.fromisoformat(start_time[:-1])
    message = f"Reminder: {event_name} at {start_time.strftime('%Y-%m-%d %H:%M')}"
    bot.send_message(chat_id=CHAT_ID, text=message)

# Function to Check Events and Schedule Reminders
def check_and_schedule():
    events = get_upcoming_events()
    now = datetime.datetime.utcnow()
    for event in events:
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        event_time = datetime.datetime.fromisoformat(start_time[:-1])
        reminder_time = event_time - datetime.timedelta(minutes=10)  # 10-min Reminder
        if now < reminder_time:
            scheduler.add_job(send_reminder, "date", run_date=reminder_time, args=[event])

# Scheduler Setup
scheduler = BackgroundScheduler()
scheduler.add_job(check_and_schedule, "interval", minutes=30)  # Check every 30 minutes
scheduler.start()

# Telegram Command to List Events
def start(update, context):
    events = get_upcoming_events()
    if not events:
        update.message.reply_text("No upcoming events found.")
    else:
        message = "Upcoming Events:\n" + "\n".join(
            [f"- {e['summary']} at {e['start']['dateTime']}" for e in events]
        )
        update.message.reply_text(message)

# Telegram Bot Setup
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))

# Start the Bot
updater.start_polling()
updater.idle()
