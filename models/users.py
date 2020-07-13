from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Set, List, Dict, Optional

from .user import User


@dataclass()
class Users(DataClassJsonMixin):
    # Dict of [twitch_user_name: user_object]
    users: Dict[str, User] = field(default_factory=lambda: {})

    # Add and delete admins/users, return True if the operation was successful, False if it wasnt (e.g. name was already a admin/user or was more powerful)
    def add_super_admin(self, user_name: str) -> bool:
        if user_name in self.users and self.users[user_name].is_superadmin:
            return False
        self.users[user_name] = User("superadmin")
        return True

    def delete_super_admin(self, user_name: str) -> bool:
        if user_name in self.users and self.users[user_name].is_superadmin:
            self.users.pop(user_name)
            return True

    def add_admin(self, user_name: str) -> bool:
        if user_name in self.users and self.users[user_name].is_at_least_admin:
            return False
        self.users[user_name] = User("admin")
        return True

    def delete_admin(self, user_name: str) -> bool:
        if user_name in self.users and self.users[user_name].is_admin:
            self.users.pop(user_name)
            return True
        return False

    def add_user(self, user_name: str) -> bool:
        if user_name in self.users and self.users[user_name].is_at_least_user:
            return False
        self.users[user_name] = User("user")
        return True

    def delete_user(self, user_name: str) -> bool:
        if user_name in self.users and self.users[user_name].is_user:
            self.users.pop(user_name)
            return True
        return False

    # SUPERADMIN COMMANDS
    def allowed_to_add_channel(self, user_name: str) -> bool:
        """ In which channels the bot should stay. """
        return user_name in self.users and self.users[user_name].is_superadmin

    def allowed_to_delete_channel(self, user_name: str) -> bool:
        return user_name in self.users and self.users[user_name].is_superadmin

    def allowed_to_add_super_admin(self, user_name: str) -> bool:
        """ Able to add superadmins to the list. """
        return user_name in self.users and self.users[user_name].is_superadmin

    def allowed_to_delete_super_admin(self, user_name: str) -> bool:
        return user_name in self.users and self.users[user_name].is_superadmin

    def allowed_to_add_admin(self, user_name: str) -> bool:
        """ Able to add admins to the list. """
        return user_name in self.users and self.users[user_name].is_superadmin

    def allowed_to_delete_admin(self, user_name: str) -> bool:
        return user_name in self.users and self.users[user_name].is_superadmin

    # ADMIN COMMANDS
    def allowed_to_add_user(self, user_name: str) -> bool:
        """ Able to add users to the list. """
        return user_name in self.users and self.users[user_name].is_at_least_admin

    def allowed_to_delete_user(self, user_name: str) -> bool:
        return user_name in self.users and self.users[user_name].is_at_least_admin

    def allowed_to_add_information(self, user_name: str) -> bool:
        """ Able to add information. """
        return user_name in self.users and self.users[user_name].is_at_least_admin

    def allowed_to_edit_information(self, user_name: str) -> bool:
        """ Able to edit information. """
        return user_name in self.users and self.users[user_name].is_at_least_admin

    def allowed_to_delete_information(self, user_name: str) -> bool:
        """ Able to delete information. """
        return user_name in self.users and self.users[user_name].is_at_least_admin

    # TWITCH USER COMMANDS
    def allowed_to_get_information(self, user_name: str) -> bool:
        """ Able to grab information about a player. """
        return user_name in self.users and self.users[user_name].is_at_least_user
