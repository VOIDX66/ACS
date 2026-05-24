import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    address: str

    def __post_init__(self):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.address):
            raise ValueError(f"Invalid email: {self.address}")

    def __str__(self) -> str:
        return self.address
