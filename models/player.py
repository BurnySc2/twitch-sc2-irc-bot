import time

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import List, Optional

from .information import Information


@dataclass()
class Player(DataClassJsonMixin):
    information: List[Information] = field(default_factory=lambda: [])

    def add_information(self, information_text: str, admin_name: str):
        new_information = Information(info=information_text, created_by=admin_name)
        self.information.append(new_information)

    def edit_information(self, information_index: int, information_text: str, admin_name: str):
        # Index out of range already checked in Players.edit_information
        assert information_index < len(self.information)

        old_information = self.information[information_index]
        old_information.modified_by = admin_name
        old_information.modified_timestamp = time.time()
        old_information.info = information_text

    def get_information_at_index(self, information_index: int) -> Optional[Information]:
        # Out of range
        if information_index >= len(self.information):
            # TODO Return error
            return None
        return self.information[information_index]
