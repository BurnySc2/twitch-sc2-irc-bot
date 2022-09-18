from twitchio.ext import commands
from twitchio import User as TwitchUser
from twitchio import Message as TwitchMessage
from twitchio.ext.commands import Context as TwitchContext


import os
import sys
import json
from pathlib import Path
from typing import List, Callable

# https://github.com/Delgan/loguru
from loguru import logger

# Remove default loggers
logger.remove()
# Log to console
logger.add(sys.stdout, level="INFO")
# Log to file, max size 5mb
logger.add("bot.log", level="INFO")

from models.channels import Channels
from models.users import Users
from models.players import Players
from models.information import Information


"""
The irc bot should be able to keep track of certain user names:
super admins - users that can remove admins and allowed users, and add other people as super admins
admins - users that can add chatters to 'allowed users' and 'admins' and also remove 'allowed users', also they can add/edit/remove information about players
allowed users - users that can grab info about a players

Commands:
!addsuperadmin <name>
!addadmin <name>
!adduser <name>
!addchannel <channel name>
^ Same with '!del... <name>'

Add or edit information of a player
!add <name> <information>
!edit <name> <new information>
Remove all information about a player
!delete <name>
Grab the information about a player
!info <name>

Files:
data/channels.json - information about which channels to initially join when the bot starts
# Dict[str, str] stands for: key = name, value = who gave him these rights
data/users.json - Dict[str, str] info about twitch chatters - who is allowed to use which commands
data/player.json - Dict[str, List[Information]] info about players
"""


class TwitchChatBot(commands.Bot):
    def __init__(self, irc_token: str, client_id: str, bot_name: str, command_prefix: str):
        self.channels_file_path = Path(__file__).parent / "data" / "channels.json"
        self.channels = Channels()
        self.load_channels()

        super().__init__(
            # Irc token to be able to connect to chat
            token=irc_token,
            # Client ID to use advanced twitch API features
            client_id=client_id,
            # The name of the bot, you need to create a second twitch account for this
            nick=bot_name,
            prefix=command_prefix,
            # The initial channels the bot is going to join, for now it will only be one channel
            initial_channels=list(self.channels.channels),
        )

        self.allow_all_users: bool = False
        self.whisper_responses: bool = False

        self.users_file_path = Path(__file__).parent / "data" / "users.json"
        self.users = Users()
        self.load_users()

        self.players_file_path = Path(__file__).parent / "data" / "players.json"
        self.players = Players()
        self.load_players()

    ############ FILE READING
    def load_channels(self):
        if self.channels_file_path.exists():
            with self.channels_file_path.open() as f:
                self.channels = Channels.from_json(f.read())

    def load_users(self):
        if self.users_file_path.exists():
            with self.users_file_path.open() as f:
                self.users = Users.from_json(f.read())

    def load_players(self):
        if self.players_file_path.exists():
            with self.players_file_path.open() as f:
                self.players = Players.from_json(f.read())

    ############ FILE WRITING
    def save_channels(self):
        os.makedirs(self.channels_file_path.parent, exist_ok=True)
        with self.channels_file_path.open("w") as f:
            f.write(self.channels.to_json(indent=4))

    def save_users(self):
        os.makedirs(self.users_file_path.parent, exist_ok=True)
        with self.users_file_path.open("w") as f:
            f.write(self.users.to_json(indent=4))

    def save_players(self):
        os.makedirs(self.players_file_path.parent, exist_ok=True)
        with self.players_file_path.open("w") as f:
            f.write(self.players.to_json(indent=4))

    ############ EVENTS
    async def event_ready(self):
        print(f"Ready | {self.nick}")

    async def event_message(self, message: TwitchMessage):
        # print(message.content)
        try:
            await self.handle_commands(message)
        except Exception as e:
            logger.trace(f"Error while receiving a message")

    ############ COMMANDS
    @commands.command(name="add", aliases=["a"])
    async def add_information(self, ctx: TwitchContext):
        author_name: str = ctx.author.name
        raw_content: str = ctx.content
        # Without the command:
        content: str = " ".join(raw_content.split(" ")[1:])

        logger.info(f"Trying to add information ({author_name}): {content}")
        if not self.users.allowed_to_add_information(author_name):
            logger.info(f"User {author_name} not allowed to add information")
            return

        player_name, *_ = content.split(" ")
        player = self.players.get_player(player_name)
        previous_information_amount = len(player.information)
        new_amount_information = self.players.add_information(author_name, content)
        if previous_information_amount != new_amount_information:
            self.save_players()
            logger.info(
                f"Added information ({previous_information_amount} -> {new_amount_information}) ({author_name}): {content}"
            )
            await ctx.send(f"Added #{new_amount_information} information for player '{player_name}'")

    @commands.command(name="edit", aliases=["e"])
    async def edit_information(self, ctx: TwitchContext):
        author_name: str = ctx.author.name
        raw_content: str = ctx.content
        # Without the command:
        content: str = " ".join(raw_content.split(" ")[1:])

        logger.info(f"Trying to edit information ({author_name}): {content}")
        if not self.users.allowed_to_edit_information(author_name):
            logger.info(f"User {author_name} not allowed to edit information")
            return

        should_save_new_players_json = self.players.edit_information(author_name, content)
        if should_save_new_players_json:
            self.save_players()
            player_name, information_index, *_ = content.split(" ")
            logger.info(f"Edited information ({author_name}): {content}")
            await ctx.send(f"Edited information at index '{information_index}' for player '{player_name}'")

    @commands.command(name="delete", aliases=["del", "d"])
    async def delete_information(self, ctx: TwitchContext):
        author: TwitchUser = ctx.author
        raw_content: str = ctx.content
        # Without the command:
        content: str = " ".join(raw_content.split(" ")[1:])

        logger.info(f"Trying to delete information ({author.name}): {content}")
        if not self.users.allowed_to_delete_information(author.name):
            logger.info(f"User {author.name} not allowed to delete information")
            return

        player_name, *_ = content.split(" ")
        if not player_name:
            # TODO Incorrect command usage
            return

        removed_player = self.players.delete_information(content)
        if removed_player:
            self.save_players()
            logger.info(f"Deleted information ({author.name}): {content}\nRemoved entry: {removed_player}")
            await ctx.send(f"Removed all information about player '{player_name}'")
            return
        await ctx.send(f"There was no information about player '{player_name}'")

    @commands.command(name="info", aliases=["i"])
    async def get_information(self, ctx: TwitchContext):
        author: TwitchUser = ctx.author
        raw_content: str = ctx.content
        # Without the command:
        content: str = " ".join(raw_content.split(" ")[1:])

        if not self.users.allowed_to_get_information(author.name):
            logger.info(f"User {author.name} not allowed to get information")
            return

        logger.info(f"Trying to get information ({author.name}): {content}")
        player_name, *rest = content.split(" ")
        player_name: str = player_name.lower()
        if not player_name:
            # Command was given but no username argument was given
            # TODO Raise error?
            return
        index = -1
        if len(rest) > 0:
            index_str, *_ = rest
            if index_str.isnumeric():
                index = int(index_str)

        if index != -1:
            # Return information about a specific index
            information: Information = self.players.get_information_at_index(player_name, index)
            response_string = f"Player '{player_name}' ({index}): {information.info_detailled}"

        else:
            # Return all information available
            information_list: List[Information] = self.players.get_information(content)
            if not information_list:
                await ctx.send(f"There was no information about player '{player_name}'")
                return

            if len(information_list) > 1:
                response_list = [
                    f"{index}) '{repr(information)}'" for index, information in enumerate(information_list)
                ]
                response_string = f"Player '{player_name}': {' | '.join(response_list)}"
            else:
                response_string = f"Player '{player_name}': {repr(information_list[0])}"

        logger.info(f"Got information ({author.name}): {content}\nResponse: {response_string}")
        # TODO What if the response string is longer than the twitch message limit?
        await ctx.send(f"{response_string}")

    @commands.command(name="listplayers", aliases=["lp"])
    async def list_all_player_names(self, ctx: TwitchContext):
        """ List all player names which the bot has information about. """
        # TODO

    @commands.command(name="listchannels", aliases=["lc"])
    async def list_all_channel_names(self, ctx: TwitchContext):
        """ List all channel names the bot is connected to. """
        # TODO

    ############ COMMANDS - Adding and removing users and channels
    async def add_remove_admin_or_user(
        self, ctx: TwitchContext, user_names: List[str], user_type: str, add: bool = True
    ):
        """ A generalized function to add or remove twitch names from admin / user list. """
        # channel: TwitchChannel = ctx.channel
        # message: TwitchMessage = ctx.message
        assert user_type in {"superadmin", "admin", "user"}
        add_permission = {
            "superadmin": self.users.allowed_to_add_super_admin,
            "admin": self.users.allowed_to_add_admin,
            "user": self.users.allowed_to_add_user,
        }
        del_permission = {
            "superadmin": self.users.allowed_to_delete_super_admin,
            "admin": self.users.allowed_to_delete_admin,
            "user": self.users.allowed_to_delete_user,
        }
        permission_function: Callable[[str], bool] = add_permission[user_type] if add else del_permission[user_type]

        # Check if command sender has permission
        author_name: TwitchUser = ctx.author
        if not permission_function(author_name.name):
            return

        logger.info(f"Trying to edit users ({ctx.author.name}): {user_names}")
        add_dict = {
            "superadmin": self.users.add_super_admin,
            "admin": self.users.add_admin,
            "user": self.users.add_user,
        }
        del_dict = {
            "superadmin": self.users.delete_super_admin,
            "admin": self.users.delete_admin,
            "user": self.users.delete_user,
        }
        add_user_function: Callable[[str], bool] = add_dict[user_type] if add else del_dict[user_type]

        added_users = []
        for user_name in user_names:
            logger.info(f"Adding {user_name} to {user_type} (command by {ctx.author.name})")
            # TODO Add information about who gave this person admin or user status
            added = add_user_function(user_name.lower())
            if added:
                added_users.append(user_name)

        if added_users:
            self.save_users()
            if add:
                await ctx.send(f"Added users with permission level '{user_type}': {', '.join(added_users)}")
            else:
                await ctx.send(f"Removed users with permission level '{user_type}': {', '.join(added_users)}")

    @commands.command(name="addsuperadmin", aliases=["addsuperadmins", "asa"])
    async def add_super_admin(self, ctx: TwitchContext):
        # Without '!addsuperadmin'
        user_names: List[str] = ctx.content.split(" ")[1:]
        await self.add_remove_admin_or_user(ctx, user_names, user_type="superadmin", add=True)

    @commands.command(name="delsuperadmin", aliases=["delsuperadmins", "dsa"])
    async def del_super_admin(self, ctx: TwitchContext):
        # Without '!delsuperadmin'
        user_names: List[str] = ctx.content.split(" ")[1:]
        await self.add_remove_admin_or_user(ctx, user_names, user_type="superadmin", add=False)

    @commands.command(name="addadmin", aliases=["addadmins", "aa"])
    async def add_admin(self, ctx: TwitchContext):
        # Without '!addadmin'
        user_names: List[str] = ctx.content.split(" ")[1:]
        await self.add_remove_admin_or_user(ctx, user_names, user_type="admin", add=True)

    @commands.command(name="deladmin", aliases=["deladmins", "da"])
    async def del_admin(self, ctx: TwitchContext):
        # Without '!deladmin'
        user_names: List[str] = ctx.content.split(" ")[1:]
        await self.add_remove_admin_or_user(ctx, user_names, user_type="admin", add=False)

    @commands.command(name="adduser", aliases=["addusers", "au"])
    async def add_user(self, ctx: TwitchContext):
        # Without '!adduser'
        content: str = " ".join(ctx.content.split(" ")[1:])
        await self.add_remove_admin_or_user(ctx, content.split(" "), user_type="user", add=True)

    @commands.command(name="deluser", aliases=["delusers", "du"])
    async def del_user(self, ctx: TwitchContext):
        # Without '!deluser'
        user_names: List[str] = ctx.content.split(" ")[1:]
        await self.add_remove_admin_or_user(ctx, user_names, user_type="user", add=False)

    @commands.command(name="addchannel", aliases=["addchannels", "ac"])
    async def add_channel(self, ctx: TwitchContext):
        # Without '!addchannel'
        channel_names: List[str] = ctx.content.split(" ")[1:]
        if not self.users.allowed_to_add_channel(ctx.author.name):
            return
        logger.info(f"Trying to add channels ({ctx.author.name}): {', '.join(channel_names)}")

        new_channels = []
        for channel_name in channel_names:
            channel_name: str = channel_name.lower()
            if channel_name not in self.channels.channels:
                logger.info(f"Adding channel ({ctx.author.name}): {channel_name}")
                new_channels.append(channel_name)
                self.channels.channels.add(channel_name)
        if new_channels:
            self.save_channels()
            await self.join_channels(new_channels)
            await ctx.send(f"Added new channels: {', '.join(new_channels)}")

    @commands.command(name="delchannel", aliases=["delchannels", "dc"])
    async def del_channel(self, ctx: TwitchContext):
        # Without '!delchannel'
        channel_names: List[str] = ctx.content.split(" ")[1:]
        if not self.users.allowed_to_delete_channel(ctx.author.name):
            return
        logger.info(f"Trying to delete channels ({ctx.author.name}): {', '.join(channel_names)}")

        new_channels = []
        for channel_name in channel_names:
            channel_name: str = channel_name.lower()
            if channel_name in self.channels.channels:
                logger.info(f"Deleting channel ({ctx.author.name}): {channel_name}")
                new_channels.append(channel_name)
                self.channels.channels.remove(channel_name)
        if new_channels:
            self.save_channels()
            await self.part_channels(new_channels)
            await ctx.send(f"Deleted channels: {', '.join(new_channels)}")


if __name__ == "__main__":
    # Load token from twitch irc token config file
    token_file_path = Path(__file__).parent / "config" / "twitch_irc_token.json"
    with open(token_file_path) as f:
        token_file_json = json.load(f)
        token = token_file_json["token"]

    # Start bot
    bot = TwitchChatBot(token, "...", "thelist_bot", "!")
    bot.run()
