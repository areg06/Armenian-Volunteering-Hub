import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.events import NewMessage
from flask import Flask
from threading import Thread
from keep_alive import keep_alive

# API credentials
API_ID = 25683175
API_HASH = '019199c087324a8791fe067d9c4b4a4d'

# Source channels (excluding the test channel)
SOURCE_CHANNELS = [
    '@unionforte',
    '@pavu_volunteers',
    '@funzone_volunteering',
    '@level_up_volunteering',
    '@powervolunteering',
]
# Target channel
TARGET_CHANNEL = '@ArmenianVolunteerHub'

# Session name
SESSION_NAME = 'batch_forwarder_session'

# Number of posts to fetch per channel
NUM_POSTS = 10
# How many days back to look
DAYS_BACK = 10

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

async def main():
    keep_alive()
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print('Client started. Fetching messages...')

    all_messages = []
    tzinfo = None

    # First, determine the timezone from the first message found
    for channel in SOURCE_CHANNELS:
        async for msg in client.iter_messages(channel, limit=1):
            tzinfo = msg.date.tzinfo
            break
        if tzinfo:
            break
    if not tzinfo:
        tzinfo = timezone.utc
    since_date = datetime.now(tzinfo) - timedelta(days=DAYS_BACK)

    for channel in SOURCE_CHANNELS:
        channel_messages = []
        async for msg in client.iter_messages(channel, limit=100):
            if msg.date < since_date:
                break
            if not msg.message and not msg.media:
                continue  # Skip empty messages
            channel_messages.append(msg)
            if len(channel_messages) >= NUM_POSTS:
                break
        print(f"Fetched {len(channel_messages)} messages from {channel}")
        all_messages.extend(channel_messages)

    # Sort all messages by date (oldest to newest)
    all_messages.sort(key=lambda m: m.date)

    print(f"Posting {len(all_messages)} opportunity links in chronological order...")
    for msg in all_messages:
        channel_username = msg.chat.username if hasattr(msg.chat, 'username') and msg.chat.username else None
        if channel_username:
            header = f"Նոր հնարավորություն @{channel_username}-ից 😉"
        else:
            channel_title = msg.chat.title if hasattr(msg.chat, 'title') and msg.chat.title else 'այս ալիքից'
            header = f"Նոր հնարավորություն {channel_title}-ից 😉"
        link = get_message_link(msg)
        if link:
            post_text = f"{header}\n👉 [Դիտե՛ք այստեղ]({link})"
        else:
            post_text = header
        try:
            await client.send_message(TARGET_CHANNEL, post_text, link_preview=False, parse_mode='md')
            print(f"Posted Armenian opportunity link for message {msg.id} from {header}")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error posting opportunity link for message {msg.id}: {e}")

    print("Done!")
    await client.disconnect()

def get_message_link(msg):
    # Only works for public channels
    if hasattr(msg.chat, 'username') and msg.chat.username:
        return f"https://t.me/{msg.chat.username}/{msg.id}"
    return None

@client.on(NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    print(f"Received new message in {event.chat.username if hasattr(event.chat, 'username') else event.chat.title}")
    # ... rest of your code ...

if __name__ == '__main__':
    asyncio.run(main()) 