from telethon import TelegramClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# Initialize Telegram Client
client = TelegramClient('session_name', api_id, api_hash)

async def list_all_chats():
    await client.start()
    print("✅ Successfully logged in!")
    
    # Fetch all dialogs (chats, groups, channels)
    dialogs = await client.get_dialogs()

    print("\n🔍 Listing All Chats:\n")
    
    for dialog in dialogs:
        chat_type = "Private Chat"
        
        if dialog.is_group:
            chat_type = "Group"
        elif dialog.is_channel:
            chat_type = "Channel"
        
        print(f"📌 {chat_type}: {dialog.name} (ID: {dialog.id})")

async def main():
    await list_all_chats()
    await client.disconnect()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
