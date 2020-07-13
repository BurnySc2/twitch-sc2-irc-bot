import arrow
import time

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Set, List, Optional

from .information import Information


@dataclass()
class Player(DataClassJsonMixin):
    information: List[Information] = field(default_factory=lambda: [])

    def add_information(self, information_text: str, admin_name: str):
        new_information = Information(info=information_text, created_by=admin_name)
        self.information.append(new_information)

    def edit_information(self, information_index: int, information_text: str, admin_name: str):
        # Out of range
        if information_index >= len(self.information):
            # TODO Return error
            return

        old_information = self.information[information_index]
        old_information.modified_by.add(admin_name)
        old_information.modified = time.time()
        old_information.info = information_text

    def get_information_at_index(self, information_index: int) -> Optional[Information]:
        # Out of range
        if information_index >= len(self.information):
            # TODO Return error
            return None
        return self.information[information_index]
