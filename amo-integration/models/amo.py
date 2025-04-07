from dataclasses import dataclass


@dataclass
class AmoContact:
    contact_id: int
    is_main_contact: bool


@dataclass
class AmoNote:
    lead_id: int
    note: str
