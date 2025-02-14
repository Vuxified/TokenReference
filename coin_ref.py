from telethon import TelegramClient, events
import re
from datetime import datetime
import json
import os
import asyncio



api_id = REDACTED  
api_hash = "REDACTED"  

BOTS_TO_MONITOR = {
    "@gem_tools_calls": {
        "title": "Gem Tools Calls",
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
    }
}

response_message = ""
collected_tokens = {}

# Global Variables
ALERT_GROUP = -1002438244257
MIN_CHANNELS_FOR_ALERT = 2

# Initialize client before main()
client = TelegramClient('session_name', api_id, api_hash)

def load_data(self):
    """Load saved tracking data if it exists"""
    try:
        if os.path.exists('coin_tracking.json'):
            with open('coin_tracking.json', 'r') as f:
                self.coin_mentions = json.load(f)
        if os.path.exists('wallet_tracking.json'):
            with open('wallet_tracking.json', 'r') as f:
                self.wallet_transactions = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")

def save_data(self):
    """Save tracking data to file"""
    try:
        with open('coin_tracking.json', 'w') as f:
            json.dump(self.coin_mentions, f)
        with open('wallet_tracking.json', 'w') as f:
            json.dump(self.wallet_transactions, f)
    except Exception as e:
        print(f"Error saving data: {e}")
        




def generate_alert_message(self, identifier, coin_data):
    """Generate alert message for a coin"""
    # Generate Bullx and Trojan links
    bullx_link = f"https://neo.bullx.io/terminal?chainId=1399811149&address={identifier}"
    trojan_link = f"https://t.me/paris_trojanbot?start=d-RickBot-{identifier}"



@client.on(events.NewMessage(chats=BOTS_TO_MONITOR))
async def my_event_handler(event):
    # Pattern to match the token address
    token_address_pattern = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
    token_match = re.search(token_address_pattern, event.message.text)
    
    if token_match:
        token_address = token_match.group(0)
        sender = event.sender.username.lower()
        
        # Define a mapping for friendly names
        name_mapping = {
            "gem_tools_calls": "Gem Tool",
            "solbixsignal": "Sol Bix Signal",
            "cabaltrackerbot": "Cabal Tracker",
            "alivetrackerbot": "Alive Tracker"
        }
        
        # Check whether the sender is one of the bots
        if f"@{sender}" in BOTS_TO_MONITOR:
            alert_text = f"{name_mapping.get(sender, sender.title())} Alerted"
        else:
            alert_text = f"{sender.title()} Alerted"
        
        if token_address not in collected_tokens:
            collected_tokens[token_address] = {
                "alerts": [alert_text],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Append the alert if it's not already present.
            if alert_text not in collected_tokens[token_address]["alerts"]:
                collected_tokens[token_address]["alerts"].append(alert_text)
                
        # Join all alerts with " and "
        output_message = " and ".join(collected_tokens[token_address]["alerts"])
        print("Output:", output_message)

async def main():
    print("Starting coin and wallet tracking bot...")
    
    # Start the client
    await client.start()
    
    # Run until disconnected
    await client.run_until_disconnected()

# if __name__ == "__main__":
#     # Run the main function
#     asyncio.run(main())
