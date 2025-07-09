import asyncio
from telethon import TelegramClient, events

# API credentials
API_ID = 25683175
API_HASH = '019199c087324a8791fe067d9c4b4a4d'

# List of source channels to monitor
SOURCE_CHANNELS = [
    '@unionforte',
    '@pavu_volunteers',
    '@funzone_volunteering',
    '@level_up_volunteering',
    '@powervolunteering',
    '@testforvol'
]
# Target channel to forward messages to
TARGET_CHANNEL = '@ArmenianVolunteerHub'

# Session name (can be any string, will create a .session file)
SESSION_NAME = 'forwarder_session'

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print('Client started. Listening for new messages...')

    @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
    async def handler(event):
        msg = event.message
        chat = await event.get_chat()
        channel_username = chat.username if hasattr(chat, 'username') and chat.username else None
        if channel_username:
            header = f"Նոր հնարավորություն @{channel_username}-ից 😉"
        else:
            channel_title = chat.title if hasattr(chat, 'title') and chat.title else 'այս ալիքից'
            header = f"Նոր հնարավորություն {channel_title}-ից 😉"
        link = get_message_link(msg, chat)
        if link:
            post_text = f"{header}\n👉 [Դիտե՛ք այստեղ]({link})"
        else:
            post_text = header
        try:
            await client.send_message(TARGET_CHANNEL, post_text, link_preview=False, parse_mode='md')
            print(f"Posted Armenian opportunity link for message {msg.id} from {header}")
        except Exception as e:
            print(f"Error posting opportunity link for message {msg.id}: {e}")

    # Run the client until disconnected, auto-reconnect on disconnect
    while True:
        try:
            await client.run_until_disconnected()
        except (OSError, ConnectionError) as e:
            print(f"Disconnected: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

def get_message_link(msg, chat):
    # Only works for public channels
    if hasattr(chat, 'username') and chat.username:
        return f"https://t.me/{chat.username}/{msg.id}"
    return None

if __name__ == '__main__':
    asyncio.run(main()) 