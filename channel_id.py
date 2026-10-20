import os
from telethon import TelegramClient, events, functions

# Your Telegram API credentials
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# Bugise's Channel ID with -100 prefix
channel_id = -1002438244257

# Initialize the client
client = TelegramClient('session_name', api_id, api_hash)

async def get_topic_ids():
    async with client:
        try:
            # Get the channel/group entity
            channel = await client.get_entity(channel_id)
            
            # Get all topics/threads in the group
            topics = await client(functions.channels.GetForumTopicsRequest(
                channel=channel,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            
            # Print topic IDs and titles
            print("\nForum Topics:")
            print("-------------")
            for topic in topics.topics:
                print(f"Topic ID: {topic.id}")
                print(f"Title: {topic.title}")
                print(f"Created at: {topic.date}")
                print("-------------")

        except Exception as e:
            print(f"Error getting topics: {e}")

async def main():
    print("Getting forum topics...")
    await get_topic_ids()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
