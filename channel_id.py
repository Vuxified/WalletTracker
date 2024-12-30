from telethon import TelegramClient, events

# Your Telegram API credentials
api_id = "REDACTED"
api_hash = "REDACTED"

# Bugise's Channel ID with -100 prefix
channel_id = -1002450316172

# Initialize the client
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=channel_id))
async def handler(event):
    try:
        # Fetch the chat details
        chat = await event.get_chat()
        chat_id = chat.id
        chat_name = chat.title if hasattr(chat, 'title') else "Unknown"

        # Print the message content and chat details
        print(f"New message in {chat_name} (ID: {chat_id}): {event.message.message}")
    except Exception as e:
        print(f"Error processing message: {e}")

async def main():
    async with client:
        print("Monitoring messages from Bugise's Channel and sub-channels...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
