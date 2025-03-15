import asyncio
from telethon import events
from telegram_client import client
from message_parser import extract_buy_data, extract_sell_data
from data_tracker import DataTracker
from error_handler import log_error

# Initialize a single tracker instance
tracker = DataTracker()


async def handle_new_message(event):
    """Process incoming messages and determine buy/sell actions."""
    try:
        message = event.message.text
        topic_id = event.message.reply_to_msg_id

        if "BUY" in message:
            buy_data = extract_buy_data(message, topic_id)
            if buy_data:
                contract_address = tracker.process_buy_message(buy_data)
                if contract_address:
                    await tracker.send_cross_reference_update(contract_address)

        elif "SELL" in message:
            sell_data = extract_sell_data(message, topic_id)
            if sell_data:
                contract_address = tracker.process_sell_message(sell_data)
                if contract_address:
                    await tracker.send_cross_reference_update(contract_address)

        else:
            print(f"Unhandled message type: {message}")

    except Exception as e:
        await log_error("Message Processing Error", str(e))


async def start_event_handler():
    """Starts the Telegram bot and listens for messages."""
    await client.start()
    print("Bot started... Listening for messages.")

    # Replace with actual channel IDs
    @client.on(events.NewMessage(chats=[-1002450316172, -1002438244257]))
    async def event_handler(event):
        await handle_new_message(event)

    await client.run_until_disconnected()
