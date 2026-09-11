from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Event:
    tick: int
    type: str
    organism_id: str | None = None
    data: dict = field(default_factory=dict)

    def format(self) -> str:
        if self.type == "EAT":
            before = self.data.get("energy_before")
            after = self.data.get("energy_after")
            apple = self.data.get("apple_id")
            return f"tick={self.tick} EAT {self.organism_id} {apple} energy {before:.0f}→{after:.0f}"
        if self.type == "DEATH":
            age = self.data.get("age")
            return f"tick={self.tick} DEATH {self.organism_id} energy=0 age={age}"
        if self.type == "APPLE_RESPAWN":
            return f"tick={self.tick} APPLE_RESPAWN {self.data.get('apple_id')} tree={self.data.get('tree_id')}"
        extra = f" {self.data}" if self.data else ""
        return f"tick={self.tick} {self.type} {self.organism_id or '-'}{extra}"


@dataclass
class Fertility:
    x: float
    y: float
    expires_at: int
