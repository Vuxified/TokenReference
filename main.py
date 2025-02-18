from telethon import TelegramClient, events, functions
import re
from datetime import datetime
import json
import os
import asyncio
from topic_getter import get_channel_topics
import csv
from datetime import datetime
ERROR_LOG_FILE = 'error_log.csv'

api_id = REDACTED  
api_hash = "REDACTED"
# Global Variables
ALERT_GROUP = -1002438244257
MIN_CHANNELS_FOR_ALERT = 2
Topic_Wallet_Tracker = 247
Topic_Testing = 826
Topic_Cross_Reference = 435


bugsie_channel = {
    'channel_id': -1002450316172,
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
    'channel_id': -1002438244257,
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
    
async def main():
    await client.start()
    # Dictionary to track wallet transactions
    cross_ref = {}
    print("Starting coin and wallet tracking bot...")
    # Start the client
    @client.on(events.NewMessage(chats=[-1002450316172, -1002438244257]))
    async def handle_new_message(event):
        try:
            print("Event Happended")
            if event.message.reply_to_msg_id in bugsie_channel['topics_id']:
                contract_address = None
                topic_id = event.message.reply_to_msg_id
                message = event.message.text
                print(message)
                is_buy = "BUY" in message
                is_sell = "SELL" in message
                if "TRANSFER" in message:
                    print("Transfer Nothing Happened")
                elif is_buy:
                    print("Buy Triggered")
                    # Extract data from buy message using regex
                    topic_name = bugsie_channel['topics_id'].get(topic_id, '')
                    contract_address = re.search(r'`([1-9A-HJ-NP-Za-km-z]{32,44})`', message).group(1)
                    wallet_name = re.search(r'\*\*([^*]+)\*\*', message).group(1)
                    token_name = re.search(r'\[BUY ([^\]]+)\]', message).group(1)
                    sol_amount = float(re.search(r'swapped \*\*([\d.]+)\*\* \[', message).group(1))
                    market_cap = re.search(r'MC\**:\s*(\$[\d.]+[KMB])', message).group(1)

                    holdings_percent = float(re.search(r'Holds: .+? \(([\d.]+)%\)', message).group(1))
                    
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
                            'total_sells': 0
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
                elif is_sell:
                    print("Sell Triggered")
                    # Extract wallet name and token name
                    topic_name = bugsie_channel['topics_id'].get(topic_id, 'Could not find topic name')
                    contract_address = re.search(r'`([1-9A-HJ-NP-Za-km-z]{32,44})`', message).group(1)
                    token_name = re.search(r'\[SELL ([^\]]+)\]', message).group(1)
                    wallet_name = re.search(r"🔹\[\*\*(.*?)\*\*\]", message).group(1)    
                    marketcap_pattern = re.search(r"\*\*MC\*\*:\s*(\$\d+\.?\d*[KMB]?)", message).group(1)
                    solana_sold_pattern = re.search(r"for\s+\*\*([\d,]+\.\d+)\*\*\s+\[\*\*SOL\*\*", message).group(1)
                    sold_percentage_pattern = re.search(r"➖Sold:\s*(\d+%)?", message).group(1)
                    pnl_result = re.search(r"""
                        PnL:.*?          # Match 'PnL:' and any characters (non-greedy)
                        \*\*([+-]?\d+\.\d+)\*\*  # Capture the PnL value (e.g., +3.39 or -0.7)
                        \s+SOL.*?        # Match 'SOL' and any characters (non-greedy)
                        \(([+-]?\d+\.\d+%)\)  # Capture the PnL percentage (e.g., +96.79% or -6.98%)
                    """, message, re.VERBOSE)
                    pnl_value = pnl_result.group(1)
                    pnl_percentage = pnl_result.group(2)

                    
                    print(f"Wallet Name: {wallet_name}")
                    print(f"Token Name: {token_name}")
                    print(f"Market Cap: ${marketcap_pattern}")
                    print(f"SOL Recieved: {solana_sold_pattern}")
                    print(f"Amount Sold Precent: {sold_percentage_pattern}")
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
                            'total_sells': 0
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
                    
                    cross_ref[contract_address]['wallet'][wallet_name]['sells'].append(sell_data)
                    cross_ref[contract_address]['wallets'][wallet_name]['total_sol_sold'] += float(solana_sold_pattern)
                    cross_ref[contract_address]['wallets'][wallet_name]['total_sells'] += 1
                    if sold_percentage_pattern == "100%":
                        del cross_ref[contract_address]['wallets'][wallet_name]
                        cross_ref[contract_address]['total_wallets'] -= 1
                        # If no wallets left, remove the token entirely
                        if cross_ref[contract_address]['total_wallets'] == 0:
                            del cross_ref[contract_address]
                    
                    print(f"Processed sell: {wallet_name} sold {token_name}")
                else:
                    print(f"Error: Please check what happened with this event: {message}")
            print(json.dumps(cross_ref, indent=2, default=str))
            print(f"Wallet: {topic_name} {wallet_name} \n")

            # Send Cross Reference Update to Private Group
            if contract_address in cross_ref and cross_ref[contract_address]['total_wallets'] > MIN_CHANNELS_FOR_ALERT:
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

        
    # await client.send_message(entity=ALERT_GROUP,message='test',reply_to=Topic_Testing)
    
  
    
    # Run until disconnected
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
