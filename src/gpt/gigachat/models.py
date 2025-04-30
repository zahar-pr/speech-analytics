from dataclasses import dataclass
from datetime import datetime


@dataclass
class GigachatToken:
    access_token: str
    expires_at: int


@dataclass
class GigachatAnswer:
    role: str
    content: str
