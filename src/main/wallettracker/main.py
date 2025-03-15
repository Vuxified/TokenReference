import asyncio
from telethon import events
from telegram_client import client
from message_parser import extract_buy_data
from data_tracker import DataTracker
from error_handler import log_error

tracker = DataTracker()


async def handle_new_message(event):
    """Handle new messages and process buy/sell events."""
    try:
        message = event.message.text
        topic_id = event.message.reply_to_msg_id

        if "BUY" in message:
            buy_data = extract_buy_data(message, topic_id)
            if buy_data:
                contract_address = tracker.process_buy_message(buy_data)
                if contract_address:
                    await tracker.send_cross_reference_update(contract_address)

    except Exception as e:
        await log_error("Message Processing Error", str(e))


async def main():
    await client.start()
    print("Bot started...")

    @client.on(events.NewMessage(chats=[-1002450316172, -1002438244257]))
    async def event_handler(event):
        await handle_new_message(event)

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
