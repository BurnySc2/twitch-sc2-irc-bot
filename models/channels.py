from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Set, List, Dict, Optional


@dataclass()
class Channels(DataClassJsonMixin):
    channels: Set[str] = field(default_factory=lambda: set())
