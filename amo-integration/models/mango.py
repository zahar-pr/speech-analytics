from dataclasses import dataclass
from pydantic import BaseModel


class MangoRequest(BaseModel):
    vpdx_api_key: str
    sign: str
    js: dict

@dataclass
class MangoRecord:
    record_id: str
    temporary_url: str

