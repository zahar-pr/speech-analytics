from dataclasses import dataclass


@dataclass
class SpeechToken:
    access_token: str
    expires_at: int


@dataclass
class SpeechFile:
    id: str


@dataclass
class SpeechTask:
    id: str


@dataclass
class SpeechStatus:
    status: str
    result_status: str
    file_id: str | None
    error: str | None
