from telethon import TelegramClient, functions
import json
import os
import asyncio
from dotenv import load_dotenv 

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
# client = TelegramClient('session_name', api_id, api_hash)

async def get_channel_topics(channel_id, client):
    """Get all topics/forums in a channel"""
    try:
        # Get the channel entity
        channel = await client.get_entity(channel_id)
        
        # Get all topics in the channel
        topics = await client(functions.channels.GetForumTopicsRequest(
            channel=channel,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100  # Adjust this number based on your needs
        ))
        
        # Print topic information
        for topic in topics.topics:
            print(f"Topic ID: {topic.id}")
            print(f"Topic Title: {topic.title}")
            print(f"Topic Created: {topic.date}")
            print("---")
        
        return topics.topics
    except Exception as e:
        print(f"Error getting topics: {e}")
        return []
    

client = TelegramClient('session_name', api_id, api_hash)
    
async def main():
    await client.start()
    await get_channel_topics(os.getenv("BUGSIE_CHANNEL"), client)
if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
