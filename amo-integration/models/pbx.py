from dataclasses import dataclass


@dataclass
class CallRecord:
    uuid: str
    url: str | None
