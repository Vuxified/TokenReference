from telethon import TelegramClient, events, functions
import re
from datetime import datetime
import json
import os
import asyncio
from topic_getter import get_channel_topics

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
        192824: 'Whale Alerts',
        192826: 'Possible bond',
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
   
# Initialize client before main()
#Note to self: use variable_name.stringify() to pretty print
client = TelegramClient('session_name', api_id, api_hash)
    
async def main():
    await client.start()
    # Dictionary to track wallet transactions
    cross_ref = {
        # Structure:
        # 'token_address': {
        #     'wallets': {
        #         'wallet_name': {
        #             'buys': [
        #                 {
        #                     'token_name': str,
        #                     'market_cap': float,
        #                     'holdings_percent': float,
        #                     'sol_amount': float,
        #                     'timestamp': datetime
        #                 }
        #             ],
        #             'sells': [
        #                 {
        #                     'token_name': str,
        #                     'amount_sold_percent': float,
        #                     'pnl': float,
        #                     'sol_received': float,
        #                     'timestamp': datetime
        #                 }
        #             ],
        #             'total_sol_bought': float,
        #             'total_sol_sold': float,
        #             'total_buys': int,
        #             'total_sells': int
        #         }
        #     },
        #     'token_name': str,
        #     'total_wallets': int
        # }
    }
    print("Starting coin and wallet tracking bot...")
    # Start the client
    @client.on(events.NewMessage(chats=[-1002450316172, -1002438244257]))
    async def handle_new_message(event):
        print("Event Happended")
        if event.message.reply_to_msg_id in bugsie_channel['topics_id']:
            print("Topics Id Matched")
            topic_id = event.message.reply_to_msg_id
            topic_name = bugsie_channel['topics_id'][topic_id]
            message = event.message.text
            print(message)
            
            contract_address = re.search(r'token/([1-9A-HJ-NP-Za-km-z]{32,44})', message).group(1)
            print(f"Token Address: {contract_address}")
            # print(message)
            # Extract data from buy message using regex
            # print("Before IF Statements")
            # is_buy = "BUY" in message
            # print(f"Bought Triggered: {is_buy}")
            is_sell = "SELL" in message
            print(f"Sell Triggered: {is_sell}")


            if "BUY" in message:
                print("Buy Triggered")
                wallet_name = re.search(r'\*\*([^*]+)\*\*', message).group(1)
                token_name = re.search(r'\[BUY ([^\]]+)\]', message).group(1)
                sol_amount = float(re.search(r'swapped \*\*([\d.]+)\*\* \[', message).group(1))
                market_cap = float(re.search(r'MC\**: \$([\d.]+)K', message).group(1)) * 1000
                holdings_percent = float(re.search(r'Holds: .+? \(([\d.]+)%\)', message).group(1))
                
                print(f"Wallet Name: {wallet_name}")
                print(f"Token Name: {token_name}")
                print(f"SOL Amount: {sol_amount}")
                print(f"Market Cap: ${market_cap:,.2f}")
                print(f"Holdings Percent: {holdings_percent}%")
                print("-" * 50)  

                # # Initialize token in cross_ref if not exists
                # if contract_address not in cross_ref:
                #     cross_ref[contract_address] = {
                #         'wallets': {},
                #         'token_name': token_name,
                #         'total_wallets': 0
                #     }
                
                # # Initialize wallet in cross_ref if not exists
                # if wallet_name not in cross_ref[contract_address]['wallets']:
                #     cross_ref[contract_address]['wallets'][wallet_name] = {
                #         'buys': [],
                #         'sells': [],
                #         'total_sol_bought': 0.0,
                #         'total_sol_sold': 0.0,
                #         'total_buys': 0,
                #         'total_sells': 0
                #     }
                #     cross_ref[contract_address]['total_wallets'] += 1
                
                # # Add buy transaction
                # buy_data = {
                #     'token_name': token_name,
                #     'market_cap': market_cap,
                #     'holdings_percent': holdings_percent,
                #     'sol_amount': sol_amount,
                #     'timestamp': datetime.now()
                # }
                
                # cross_ref[contract_address]['wallets'][wallet_name]['buys'].append(buy_data)
                # cross_ref[contract_address]['wallets'][wallet_name]['total_sol_bought'] += sol_amount
                # cross_ref[contract_address]['wallets'][wallet_name]['total_buys'] += 1
                
                print(f"Processed buy: {wallet_name} bought {token_name}")
        elif is_sell:
            print("Sell Triggered")
            # Extract wallet name and token name
            first_line = message.split('\n')[1]
            wallet_name = first_line.split(' on ')[0]
            token_name = first_line.split(' on ')[1]
            sol_received = float(re.search(r'for ([\d.]+) SOL', message).group(1))
            amount_sold_percent = float(re.search(r'Sold: (\d+)%', message).group(1))
            pnl = float(re.search(r'PnL: \+([\d.]+) SOL', message).group(1))
            
            
            print(f"Wallet Name: {wallet_name}")
            print(f"Token Name: {token_name}")
            print(f"SOL Recieved: {sol_received}")
            print(f"Amount Sold Precent: ${amount_sold_percent:,.2f}")
            print(f"PNL: {pnl}%")
            print("-" * 50)  
            # if contract_address not in cross_ref:
            #     cross_ref[contract_address] = {
            #         'wallets': {},
            #         'token_name': token_name,
            #         'total_wallets': 0
            #     }
            
            # # Initialize wallet in cross_ref if not exists
            # if wallet_name not in cross_ref[contract_address]['wallets']:
            #     cross_ref[contract_address]['wallets'][wallet_name] = {
            #         'buys': [],
            #         'sells': [],
            #         'total_sol_bought': 0.0,
            #         'total_sol_sold': 0.0,
            #         'total_buys': 0,
            #         'total_sells': 0
            #     }
            #     cross_ref[contract_address]['total_wallets'] += 1
            
            # # Add sell transaction
            # sell_data = {
            #     'token_name': token_name,
            #     'amount_sold_percent': amount_sold_percent,
            #     'pnl': pnl,
            #     'sol_received': sol_received,
            #     'timestamp': datetime.now()
            # }
            
            # cross_ref[contract_address]['wallets'][wallet_name]['sells'].append(sell_data)
            # cross_ref[contract_address]['wallets'][wallet_name]['total_sol_sold'] += sol_received
            # cross_ref[contract_address]['wallets'][wallet_name]['total_sells'] += 1
            
            print(f"Processed sell: {wallet_name} sold {token_name}")
        else:
            print(f"Error: Please check what happened with this event: {message}")
            
        
    # await client.send_message(entity=ALERT_GROUP,message='test',reply_to=Topic_Testing)
    
  
    
    # Run until disconnected
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
