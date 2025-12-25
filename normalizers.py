from datetime import datetime
from email_model import NormalizedEmail


def normalize_email(raw_email: dict) -> NormalizedEmail:
    return NormalizedEmail(
        message_id=raw_email["id"],
        sender=normalize_sender(raw_email["from"]),
        subject=raw_email["subject"].strip(),
        snippet=raw_email["snippet"].strip(),
        received_at=normalize_timestamp(raw_email["timestamp"])
    )



def normalize_timestamp(ms_timestamp: str) -> datetime:
    try:
        return datetime.fromtimestamp(int(ms_timestamp) / 1000)
    except Exception:
        return None
    
def normalize_sender(raw_from: str) -> str:
    if "<" in raw_from:
        return raw_from.split("<")[0].strip()
    return raw_from.strip()

