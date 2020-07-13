from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Set, List, Dict, Optional

from twitchio.dataclasses import User as TwitchUser
from twitchio.dataclasses import Channel as TwitchChannel
from twitchio.dataclasses import Message as TwitchMessage
from twitchio.dataclasses import Context as TwitchContext

from .player import Player
from .information import Information


@dataclass()
class Players(DataClassJsonMixin):
    # Dict of [player_name: player_object]
    players: Dict[str, Player] = field(default_factory=lambda: {})

    def get_player(self, player_name: str) -> Player:
        """ Tries to return the player from the database. If it doesn't exist, create a new one. """
        if player_name in self.players:
            return self.players.get(player_name)
        new_player = Player()
        self.players[player_name] = new_player
        return new_player

    def add_information(self, author_name: str, content_string: str) -> bool:
        # Split content: head (player name) and rest (player information)
        player_name, *new_information = content_string.split(" ")
        new_information = " ".join(new_information)

        if not new_information:
            # TODO Add error: player_name is empty or new_information is empty = incorrect command usage
            return False

        player = self.get_player(player_name)
        player.add_information(new_information, author_name)
        return True

    def edit_information(self, author_name: str, content_string: str) -> bool:
        # Split content: head (player name), index and rest (player information)
        player_name: str
        information_index: str
        player_name, information_index, *new_information = content_string.split(" ")
        new_information = " ".join(new_information)

        if not new_information:
            # TODO Add error: player_name is empty or new_information is empty = incorrect command usage
            return False

        if not information_index.isnumeric():
            # TODO Add error: information index is not a number
            return False

        player = self.get_player(player_name)
        player.edit_information(int(information_index), new_information, author_name)
        return True

    def delete_information(self, content_string: str) -> bool:
        # Split content: head (player name) and rest (player information)
        player_name: str
        player_name, *_ = content_string.split(" ")

        if not player_name:
            # TODO Add error: player_name is empty or new_information is empty = incorrect command usage
            return False

        return bool(self.players.pop(player_name, None))

    def get_information(self, player_name: str) -> List[Information]:
        if player_name in self.players:
            return self.players[player_name].information
        return []

    def get_information_at_index(self, player_name: str, index: int = -1) -> Information:
        return self.get_information(player_name)[index]
