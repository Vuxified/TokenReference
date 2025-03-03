from telethon import TelegramClient, events, functions
import re
from datetime import datetime
import json
import os
import asyncio
from topic_getter import get_channel_topics
import csv
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
ALERT_GROUP = int(os.getenv("ALERT_GROUP"))  # Convert to int if necessary
MIN_CHANNELS_FOR_ALERT = 2
Topic_Wallet_Tracker = 247
Topic_Testing = 826
Topic_Cross_Reference = 435

ERROR_LOG_FILE = 'error_log.csv'

bugsie_channel = {
    'channel_id': os.getenv("BUGSIE_CHANNEL"),
    'topics_id': {
        13: 'Influencer / KOLs',
        2215: 'Insiders + Whales',
        15: '100-80% Winrate',
        9: 'Notable Token Deployer Addresses',
        # 192824: 'Whale Alerts',
        # 192826: 'Possible bond',
    },
}

personal_tele = {
    'channel_id': os.getenv("ALERT_GROUP"),
    'topics_id': {
        826: 'Testing',
        2215: 'Cross Reference',
        15: 'Wallet Tracker',
    },
}

after_bond_tracker = {
    'channel_id': -1002347611734,
    'topics_id': {
        1: 'First Signal',
        3: 'Transactions After Signal',
        4071: 'Called 5+  in Bond Tracker',
        6516: 'Called 10+ in Bond Tracker',
        12025: 'Called 2+ in Bond Tracker'
    }
}

# Create error log file if it doesn't exist
if not os.path.exists(ERROR_LOG_FILE):
    with open(ERROR_LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Error Type', 'Message', 'Details'])

async def log_error(error_type, message, details=""):
    """Log error to CSV file"""
    with open(ERROR_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(),
            error_type,
            message,
            details
        ])
   
# Initialize client before main()
#Note to self: use variable_name.stringify() to pretty print
client = TelegramClient('session_name', api_id, api_hash)
    
def initialize_cross_ref():
    """Initialize the cross reference dictionary."""
    return {}

def extract_buy_data(message, topic_id):
    """Extract relevant data from a buy message."""
    topic_name = bugsie_channel['topics_id'].get(topic_id, '')
    contract_address = re.search(r'`([1-9A-HJ-NP-Za-km-z]{32,44})`', message).group(1)
    wallet_name = re.search(r'\*\*([^*]+)\*\*', message).group(1)
    token_name = re.search(r'\[BUY ([^\]]+)\]', message).group(1)
    sol_amount = float(re.search(r'swapped \*\*([\d.]+)\*\* \[', message).group(1))
    market_cap = re.search(r'MC\**:\s*(\$[\d.]+[KMB])', message).group(1)
    holdings_percent = float(re.search(r'Holds: .+? \(([\d.]+)%\)', message).group(1))

    return {
        'topic_name': topic_name,
        'contract_address': contract_address,
        'wallet_name': wallet_name,
        'token_name': token_name,
        'sol_amount': sol_amount,
        'market_cap': market_cap,
        'holdings_percent': holdings_percent
    }

async def process_buy_message(data, cross_ref):
    """Process a buy message and update cross_ref."""
    topic_name = data['topic_name']
    contract_address = data['contract_address']
    wallet_name = data['wallet_name']
    token_name = data['token_name']
    sol_amount = data['sol_amount']
    market_cap = data['market_cap']
    holdings_percent = data['holdings_percent']

    print(f"Wallet Name: {wallet_name}")
    print(f"Token Name: {token_name}")
    print(f"SOL Amount: {sol_amount}")
    print(f"Market Cap: {market_cap}")
    print(f"Holdings Percent: {holdings_percent}%")
    print("-" * 50)

    # Initialize token in cross_ref if not exists
    if contract_address not in cross_ref:
        cross_ref[contract_address] = {
            'wallets': {},
            'token_name': token_name,
            'total_wallets': 0
        }

    # Initialize wallet in cross_ref if not exists
    if wallet_name not in cross_ref[contract_address]['wallets']:
        cross_ref[contract_address]['wallets'][wallet_name] = {
            'buys': [],
            'sells': [],
            'total_sol_bought': 0.0,
            'total_sol_sold': 0.0,
            'total_buys': 0,
            'total_sells': 0,
            'topic_name': topic_name
        }
        cross_ref[contract_address]['total_wallets'] += 1

    # Add buy transaction
    buy_data = {
        'token_name': token_name,
        'market_cap': market_cap,
        'holdings_percent': holdings_percent,
        'sol_amount': sol_amount,
        'timestamp': datetime.now(),
        'topic_name': topic_name
    }

    cross_ref[contract_address]['wallets'][wallet_name]['buys'].append(buy_data)
    cross_ref[contract_address]['wallets'][wallet_name]['total_sol_bought'] += sol_amount
    cross_ref[contract_address]['wallets'][wallet_name]['total_buys'] += 1

    print(f"Processed buy: {wallet_name} bought {token_name}")

    # Check if we need to send a message
    if cross_ref[contract_address]['total_wallets'] >= MIN_CHANNELS_FOR_ALERT:
        await send_cross_reference_update(contract_address, cross_ref)

def extract_sell_data(message, topic_id):
    """Extract relevant data from a sell message."""
    topic_name = bugsie_channel['topics_id'].get(topic_id, 'Could not find topic name')
    contract_address_match = re.search(r'`([1-9A-HJ-NP-Za-km-z]{32,44})`', message)

    if contract_address_match:
        contract_address = contract_address_match.group(1)
    else:
        print("Error: Contract address not found in message.")
        return None

    wallet_name = re.search(r"🔹\[\*\*(.*?)\*\*\]", message).group(1)
    token_name = re.search(r'\[SELL ([^\]]+)\]', message).group(1)
    marketcap_pattern = re.search(r"\*\*MC\*\*:\s*(\$\d+\.?\d*[KMB]?)", message).group(1)

    # Check for solana_sold_pattern with error handling
    solana_sold_pattern_match = re.search(r"for\s+\*\*([\d,]+\.\d+)\*\*\s+\[\*\*SOL\*\*", message)
    if solana_sold_pattern_match:
        solana_sold_pattern = solana_sold_pattern_match.group(1)
    else:
        print("Error: SOL amount sold not found in message.")
        solana_sold_pattern = "0"  # Default value or handle as needed

    sold_percentage_pattern = re.search(r"➖Sold:\s*(\d+%)?", message)
    if sold_percentage_pattern:
        sold_percentage_pattern = sold_percentage_pattern.group(1)
    else:
        sold_percentage_pattern = "0%"  # Default value or handle as needed

    pnl_result = re.search(r"""
        PnL:.*?          # Match 'PnL:' and any characters (non-greedy) THANKS CHATGPT
        \*\*([+-]?\d+\.\d+)\*\*  # Capture the PnL value (e.g., +3.39 or -0.7)
        \s+SOL.*?        # Match 'SOL' and any characters (non-greedy)
        \(([+-]?\d+\.\d+%)\)  # Capture the PnL percentage (e.g., +96.79% or -6.98%)
    """, message, re.VERBOSE)

    if pnl_result:
        pnl_value = pnl_result.group(1)
        pnl_percentage = pnl_result.group(2)
    else:
        pnl_value = "0"
        pnl_percentage = "0%"  # Default values or handle as needed

    return {
        'topic_name': topic_name,
        'contract_address': contract_address,
        'wallet_name': wallet_name,
        'token_name': token_name,
        'marketcap_pattern': marketcap_pattern,
        'solana_sold_pattern': solana_sold_pattern,
        'sold_percentage_pattern': sold_percentage_pattern,
        'pnl_value': pnl_value,
        'pnl_percentage': pnl_percentage
    }

def process_sell_message(data, cross_ref):
    """Process a sell message and update cross_ref."""
    topic_name = data['topic_name']
    contract_address = data['contract_address']
    wallet_name = data['wallet_name']
    token_name = data['token_name']
    marketcap_pattern = data['marketcap_pattern']
    solana_sold_pattern = data['solana_sold_pattern']
    sold_percentage_pattern = data['sold_percentage_pattern']
    pnl_value = data['pnl_value']
    pnl_percentage = data['pnl_percentage']

    print(f"Wallet Name: {wallet_name}")
    print(f"Token Name: {token_name}")
    print(f"Market Cap: ${marketcap_pattern}")
    print(f"SOL Received: {solana_sold_pattern}")
    print(f"Amount Sold Percent: {sold_percentage_pattern}")
    print(f"PNL: {pnl_value}%, PNL Percentage: {pnl_percentage}")
    print("-" * 50)

    if contract_address not in cross_ref:
        cross_ref[contract_address] = {
            'wallets': {},
            'token_name': token_name,
            'total_wallets': 0
        }

    # Initialize wallet in cross_ref if not exists
    if wallet_name not in cross_ref[contract_address]['wallets']:
        cross_ref[contract_address]['wallets'][wallet_name] = {
            'buys': [],
            'sells': [],
            'total_sol_bought': 0.0,
            'total_sol_sold': 0.0,
            'total_buys': 0,
            'total_sells': 0,
            'topic_name': topic_name
        }
        cross_ref[contract_address]['total_wallets'] += 1

    # Add sell transaction
    sell_data = {
        'token_name': token_name,
        'amount_sold_percent': sold_percentage_pattern,
        'sol pnl': pnl_value,
        'pnl_percentage': pnl_percentage,
        'sol_received': solana_sold_pattern,
        'timestamp': datetime.now(),
        'topic_name': topic_name
    }

    cross_ref[contract_address]['wallets'][wallet_name]['sells'].append(sell_data)
    cross_ref[contract_address]['wallets'][wallet_name]['total_sol_sold'] += float(solana_sold_pattern)
    cross_ref[contract_address]['wallets'][wallet_name]['total_sells'] += 1

    if sold_percentage_pattern == "100%":
        del cross_ref[contract_address]['wallets'][wallet_name]
        cross_ref[contract_address]['total_wallets'] -= 1
        # If no wallets left, remove the token entirely
        if cross_ref[contract_address]['total_wallets'] == 0:
            del cross_ref[contract_address]

    print(f"Processed sell: {wallet_name} sold {token_name}")

async def send_cross_reference_update(contract_address, cross_ref):
    """Send a cross-reference update message to the Telegram group."""
    token_data = cross_ref[contract_address]
    message = f"🔄 Cross Reference Update for {token_data['token_name']}\n"
    message += f"📊 Total Wallets Tracking: {token_data['total_wallets']}\n"
    message += f"📍 Contract: `{contract_address}`\n\n"

    for wallet, stats in token_data['wallets'].items():
        message += f"👛 Wallet: {stats['topic_name']} {wallet} \n"
        message += f"   • Total SOL Bought: {stats['total_sol_bought']:.3f}\n"
        message += f"   • Total SOL Sold: {stats['total_sol_sold']:.3f}\n"

        # Add latest buy info if exists
        if stats['buys']:
            latest_buy = stats['buys'][-1]
            message += f"   📈 Latest Buy:\n"
            message += f"      Market Cap: {latest_buy['market_cap']}\n"
            message += f"      Holdings: {latest_buy['holdings_percent']}%\n"

        # Add latest sell info if exists
        if stats['sells']:
            latest_sell = stats['sells'][-1]
            message += f"   📉 Latest Sell:\n"
            message += f"      Amount Sold: {latest_sell['amount_sold_percent']}\n"
            message += f"      SOL PnL: {latest_sell['sol pnl']} SOL\n"
            message += f"      PnL %: {latest_sell['pnl_percentage']}\n"
            message += f"      SOL Received: {latest_sell['sol_received']}\n"

        message += "\n"

    await client.send_message(
        entity=ALERT_GROUP,
        message=message,
        reply_to=Topic_Testing
    )

async def handle_new_message(event, cross_ref):
    """Handle new messages and process buy/sell events."""
    try:
        print("Event Happened")
        if event.message.reply_to_msg_id in bugsie_channel['topics_id']:
            topic_id = event.message.reply_to_msg_id
            message = event.message.text
            print(message)

            if "TRANSFER" in message:
                print("Transfer Nothing Happened")
            elif "BUY" in message:
                buy_data = extract_buy_data(message, topic_id)
                await process_buy_message(buy_data, cross_ref)

            elif "SELL" in message:
                sell_data = extract_sell_data(message, topic_id)
                if sell_data:
                    process_sell_message(sell_data, cross_ref)

                    # Check if we need to send a message
                    if sell_data['contract_address'] in cross_ref and cross_ref[sell_data['contract_address']]['total_wallets'] >= MIN_CHANNELS_FOR_ALERT:
                        await send_cross_reference_update(sell_data['contract_address'], cross_ref)

            else:
                print(f"Error: Please check what happened with this event: {message}")

            print(json.dumps(cross_ref, indent=2, ensure_ascii=False, default=str))

    except Exception as e:
        import traceback
        error_message = f"Error processing message: {str(e)}"
        error_traceback = traceback.format_exc()

        print("=" * 50)
        print("ERROR DETAILS:")
        print(f"Message: {error_message}")
        print("\nTraceback:")
        print(error_traceback)
        print("=" * 50)

        await log_error(
            "Message Processing Error",
            event.message.text if hasattr(event, 'message') else "No message text",
            error_traceback
        )

async def main():
    await client.start()
    cross_ref = initialize_cross_ref() 
    print("Starting coin and wallet tracking bot...")

    @client.on(events.NewMessage(chats=[-1002450316172, -1002438244257]))
    async def event_handler(event):
        await handle_new_message(event, cross_ref)

    # Run until disconnected
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
