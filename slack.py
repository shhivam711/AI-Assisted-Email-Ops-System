import requests
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_alert(message: str):
    payload = {
        "text": message
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    
    if not SLACK_WEBHOOK_URL:
        raise RuntimeError("Slack webhook URL not configured")

    if response.status_code != 200:
        print("Slack error:", response.text)


    
