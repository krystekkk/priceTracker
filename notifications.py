import json
from datetime import datetime

NOTIFICATION_FILE = "last_notification.json"


def save_last_notification(date):
    with open(NOTIFICATION_FILE, "w") as file:
        json.dump({"last_notification": date.isoformat()}, file)


def load_last_notification():
    try:
        with open(NOTIFICATION_FILE, "r") as file:
            data = json.load(file)
            return datetime.fromisoformat(data["last_notification"])
    except:
        return None
