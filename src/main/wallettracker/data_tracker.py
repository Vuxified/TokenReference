from datetime import datetime
import json
from config import MIN_CHANNELS_FOR_ALERT
from telegram_client import client
from config import ALERT_GROUP


class DataTracker:
    def __init__(self):
        self.cross_ref = {}

    def process_buy_message(self, data):
        """Process a buy message and update tracking data."""
        contract_address = data['contract_address']
        wallet_name = data['wallet_name']

        if contract_address not in self.cross_ref:
            self.cross_ref[contract_address] = {
                'wallets': {}, 'token_name': data['token_name'], 'total_wallets': 0}

        if wallet_name not in self.cross_ref[contract_address]['wallets']:
            self.cross_ref[contract_address]['wallets'][wallet_name] = {
                'buys': [], 'total_sol_bought': 0.0, 'total_buys': 0}
            self.cross_ref[contract_address]['total_wallets'] += 1

        # Store transaction
        self.cross_ref[contract_address]['wallets'][wallet_name]['buys'].append(
            data)
        self.cross_ref[contract_address]['wallets'][wallet_name]['total_sol_bought'] += data['sol_amount']
        self.cross_ref[contract_address]['wallets'][wallet_name]['total_buys'] += 1

        if self.cross_ref[contract_address]['total_wallets'] >= MIN_CHANNELS_FOR_ALERT:
            return contract_address  # Flag for alert
        return None

    async def send_cross_reference_update(self, contract_address):
        """Send an alert if enough wallets are tracking the token."""
        token_data = self.cross_ref[contract_address]
        message = f"🔄 Cross Reference Update for {token_data['token_name']}\n"
        message += f"📊 Total Wallets Tracking: {token_data['total_wallets']}\n📍 Contract: `{contract_address}`\n"

        for wallet, stats in token_data['wallets'].items():
            message += f"👛 Wallet: {wallet} \n   • Total SOL Bought: {stats['total_sol_bought']:.3f}\n"

        await client.send_message(entity=ALERT_GROUP, message=message)
