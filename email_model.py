from dataclasses import dataclass
from datetime import datetime


@dataclass
class NormalizedEmail:
    message_id: str
    sender: str
    subject: str
    snippet: str
    received_at: datetime
