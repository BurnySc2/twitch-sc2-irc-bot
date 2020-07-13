import arrow
import time

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Set, List, Optional


@dataclass()
class User(DataClassJsonMixin):
    # One of: "superadmin", "admin", "user"
    type: str

    @property
    def is_superadmin(self) -> bool:
        return self.type == "superadmin"

    @property
    def is_admin(self) -> bool:
        return self.type == "admin"

    @property
    def is_user(self) -> bool:
        return self.type == "user"

    @property
    def is_at_least_user(self) -> bool:
        return self.is_superadmin or self.is_admin or self.is_user

    @property
    def is_at_least_admin(self) -> bool:
        return self.is_superadmin or self.is_admin
