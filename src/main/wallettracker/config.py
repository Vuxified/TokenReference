import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
ALERT_GROUP = int(os.getenv("ALERT_GROUP"))

MIN_CHANNELS_FOR_ALERT = 2
ERROR_LOG_FILE = 'error_log.csv'

BUGSIE_CHANNEL = {
    'channel_id': os.getenv("BUGSIE_CHANNEL"),
    'topics_id': {
        13: 'Influencer / KOLs',
        2215: 'Insiders + Whales',
        15: '100-80% Winrate',
        9: 'Notable Token Deployer Addresses',
    },
}

PERSONAL_TELE = {
    'channel_id': os.getenv("ALERT_GROUP"),
    'topics_id': {
        826: 'Testing',
        2215: 'Cross Reference',
        15: 'Wallet Tracker',
    },
}
