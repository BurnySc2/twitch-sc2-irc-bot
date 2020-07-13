import arrow
import time

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Set, List, Optional


@dataclass()
class Information(DataClassJsonMixin):
    # The actual piece of information
    info: str
    # Who created the information
    created_by: str
    # When the information was created
    created_timestamp: int = field(default_factory=lambda: time.time())
    # Who modified this entry
    modified_by: Optional[str] = None
    # When it was last modified
    modified_timestamp: Optional[int] = None

    def __repr__(self) -> str:
        return self.info

    @property
    def info_detailled(self) -> str:
        last_modified_name = self.created_by if not self.modified_by else self.modified_by
        last_modified_time: arrow.Arrow = arrow.get(
            self.created_timestamp
        ) if not self.modified_timestamp else arrow.get(self.modified_timestamp)
        return f"'{self.info}' was last modified by '{last_modified_name}' on {last_modified_time} which was {last_modified_time.humanize()}."
