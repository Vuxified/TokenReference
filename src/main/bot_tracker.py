from telethon import TelegramClient, events, functions
import re
from datetime import datetime
import json
import os
import asyncio
from src.test.topic_getter import get_channel_topics
import csv
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
AFTER_BOND_CHANNEL_ID = int(os.getenv("AFTER_BOND_CHANNEL_ID"))
ALERT_GROUP = int(os.getenv("ALERT_GROUP"))
MIN_CHANNELS_FOR_ALERT = 2
Topic_Wallet_Tracker = 247
Topic_Testing = 826
Topic_Cross_Reference = 435


# Bot Tracker Class
class BotTracker:
    def __init__(self):
        # This will keep track of all tokens
        self.token_calls = {}

    def add_bot(self, bot_name, bot_ca):
        if bot_ca not in self.token_calls:
            self.token_calls[bot_ca] = {}
        if bot_name not in self.token_calls[bot_ca]:
            self.token_calls[bot_ca][bot_name] = 0
        self.token_calls[bot_ca][bot_name] += 1

        self.check_requirements(bot_name, bot_ca)

    # Checks to see if it needs to send an alert to telegram
    def check_requirements(self, bot_name, message):

        bot_ca = self.find_token(message)
        print(f"Find Token Results: {bot_ca}")
        total_calls = sum(self.token_calls[bot_ca].values())
        total_bots_call = len(self.token_calls[bot_ca])
        # print(self.token_calls[bot_ca])
        # print(f"Total number of bots called token {bot_ca} {total_bots_call} times")
        # print(f"This bot has a total of {total_calls}")
        if total_bots_call >= 2 and total_calls >= 2:
            print(f"{bot_ca}  has been called {total_calls} times")

    def find_token(self, message):
        solana_ca = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")
        match = solana_ca.search(message)

        if match:
            print(f"Returning match.group {match.group()}")
            return match.group()
        else:
            print(f"Returning None, Couldn't find CA")
            return None


# print(f"After Bond Channel ID {AFTER_BOND_CHANNEL_ID}")
BOTS_TO_MONITOR = {
    "@gem_tools_calls": {
        "title": "Gem Tools Calls",
        "date_called": None,
        "market_cap": None
    },

    "@gemtools_gambles": {
        "title": "Gem Tools Gambles",
        "date_called": None,
        "market_cap": None
    },

    "@solbixsignal": {
        "title": "Solbix Signal",
        "date_called": None,
        "market_cap": None
    },
    "@cabaltrackerbot": {
        "title": "Cabal Tracker Bot",
        "date_called": None,
        "market_cap": None
    },
    "@alivetrackerbot": {
        "title": "Alive Tracker Bot",
        "date_called": None,
        "market_cap": None
    },
    "@MoonshotMCAlertBot": {
        "title": "Moonshot MC Alert Bot",
        "date_called": None,
        "market_cap": None
    },

    "@RaydiumMCAlertBot": {
        "title": "Raydium Alert Bot",
        "date_called": None,
        "market_cap": None
    },


}


AFTER_BOND_MONITOR = {
    # Topic IDs
    "28350": {
        "title": "First Signal"
    },
    "3": {
        "title": "Transactions after signal"
    },
    "12025": {
        "title": "Activity 2+"
    },
    "4071": {
        "title": "Activity 5+"
    },
    "6516": {
        "title": "Activity 10+"
    },
    "2": {
        "title": "Initial Call Activity Tracker"
    }
}

MONITORED_TOPICS = set(AFTER_BOND_MONITOR.keys())


client = TelegramClient('session_name', api_id, api_hash)


async def get_channel_entity():
    """ Fetch the channel entity to ensure the bot has access. """
    print(f"🔍 Fetching channel entity for ID: {AFTER_BOND_CHANNEL_ID}")

    try:
        entity = await client.get_entity(AFTER_BOND_CHANNEL_ID)
        print(
            f"✅ Successfully found channel: {entity.title} (ID: {entity.id})")
        return entity
    except Exception as e:
        print(f"🚨 Error: {e} - Ensure the bot/user has access to the channel.")
        return None


@client.on(events.NewMessage(chats=AFTER_BOND_CHANNEL_ID))
async def message_handler(event):
    """ Process and print only messages that match monitored topics. """
    message = event.message
    topic_id = str(message.reply_to_msg_id)
    if topic_id in AFTER_BOND_MONITOR:
        print(
            f"Found Topic {topic_id} Bond Monitor: {AFTER_BOND_MONITOR[topic_id]}")
        print(f"Message ID: {message.id} \n Message Full Output: {message} ")


async def main():
    """ Start the client and monitor messages. """
    await client.start()
    print("✅ Successfully logged into Telegram!")

    entity = await get_channel_entity()
    if entity:
        print(f"🔍 Monitoring messages in: {entity.title}")

    await client.run_until_disconnected()


if __name__ == "__main__":
    client.loop.run_until_complete(main())
