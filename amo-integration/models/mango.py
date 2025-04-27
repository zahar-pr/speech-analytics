from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class MangoRecord:
    record_id: str
    temporary_url: str

