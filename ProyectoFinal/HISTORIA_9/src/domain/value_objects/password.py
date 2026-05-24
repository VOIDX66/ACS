from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    hash: str

    @staticmethod
    def validate(raw: str) -> None:
        if len(raw) < 8:
            raise ValueError("Password must be at least 8 characters")
