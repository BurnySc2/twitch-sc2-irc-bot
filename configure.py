from pathlib import Path
import os

from models.channels import Channels
from models.users import Users


def set_up_channels():
    channels_file_path = Path(__file__).parent / "data" / "channels.json"

    channels_to_join = []
    input_channel_name = None
    while input_channel_name is None or input_channel_name != "":
        input_channel_name = input(f"What channel should this bot join initially? ")
        if input_channel_name == "":
            break
        assert " " not in input_channel_name
        channels_to_join.append(input_channel_name)

    channels_object = Channels.from_dict({"channels": channels_to_join})
    os.makedirs(channels_file_path.parent, exist_ok=True)
    with channels_file_path.open("w") as f:
        f.write(channels_object.to_json(indent=4))


def set_up_super_admins():
    users_file_path = Path(__file__).parent / "data" / "users.json"

    users_as_superadmin = []
    input_user_name = None
    users_object = Users()
    while input_user_name is None or input_user_name != "":
        input_user_name = input(f"What user name should be super admin? ")
        if input_user_name == "":
            break
        assert " " not in input_user_name
        users_object.add_super_admin(input_user_name)

    os.makedirs(users_file_path.parent, exist_ok=True)
    with users_file_path.open("w") as f:
        f.write(users_object.to_json(indent=4))


if __name__ == "__main__":
    set_up_channels()
    set_up_super_admins()
