import re
from datetime import datetime
from config import BUGSIE_CHANNEL


def extract_buy_data(message, topic_id):
    """Extract relevant data from a buy message."""
    topic_name = BUGSIE_CHANNEL['topics_id'].get(topic_id, 'Unknown')
    contract_address_match = re.search(
        r'`([1-9A-HJ-NP-Za-km-z]{32,44})`', message)
    wallet_name_match = re.search(r'\*\*([^*]+)\*\*', message)
    token_name_match = re.search(r'\[BUY ([^\]]+)\]', message)
    sol_amount_match = re.search(r'swapped \*\*([\d.]+)\*\* \[', message)
    market_cap_match = re.search(r'MC\**:\s*(\$[\d.]+[KMB])', message)
    holdings_percent_match = re.search(r'Holds: .+? \(([\d.]+)%\)', message)

    if not all([contract_address_match, wallet_name_match, token_name_match, sol_amount_match, market_cap_match, holdings_percent_match]):
        return None  # Invalid message format

    return {
        'topic_name': topic_name,
        'contract_address': contract_address_match.group(1),
        'wallet_name': wallet_name_match.group(1),
        'token_name': token_name_match.group(1),
        'sol_amount': float(sol_amount_match.group(1)),
        'market_cap': market_cap_match.group(1),
        'holdings_percent': float(holdings_percent_match.group(1))
    }
