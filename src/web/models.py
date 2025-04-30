from dataclasses import dataclass
from pydantic import BaseModel


class MangoRequest(BaseModel):
    vpbx_api_key: str
    sign: str
    js: dict


class TelephonesList(BaseModel):
    telephones: list[str]
