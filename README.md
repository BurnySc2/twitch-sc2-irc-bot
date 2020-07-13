# A twitch irc bot to keep track of what SC2 players do

TODO Write the readme

# Commands

### Player information

#### !add \<player name\>

alias: !a

Adds information to the player name. Each player can have a list of information

#### !edit \<player name\> \<information index\>

alias: !e

Edits an information entry of a player. 

Example: 
    
    !edit uthermal 0 macro god

which edits the first information entry

#### !delele \<player name\>

alias: !del, !d

Deletes all information of a player

#### !info \<player name\> \<information index\>

alias: !i

Retrieves all the information of a player. If information index is given, will retrieve only the specific information and information of who edited that piece of information and when

### Adding admins and users

#### !addsuperadmin \<twitch user name\>

alias: !addsuperadmins, !asa

Adds all usernames after the command to the super admins. See 'Permissions' on what superadmins can do

#### !delsuperadmin \<twitch user name\>

alias: !delsuperadmins, !dsa

Opposite of above

#### !addadmin \<twitch user name\>

alias: !addadmins , !aa

Adds all usernames after the command to the admins. See 'Permissions' on what admins can do

#### !deladmin \<twitch user name\>

alias: !deladmins, !da

Opposite of above

#### !adduser \<twitch user name\>

alias: !addusers , !au

Adds all usernames after the command to the admins. See 'Permissions' on what users can do

#### !deluser \<twitch user name\>

alias: !delusers, !du

Opposite of above

### Adding channels

#### !addchannel \<channel name\>

alias: !addchannels, !ac

Adds the bot to the specified channels. The bot will listen to commands in those channel.

#### !delchannel \<channel name\>

alias: !delchannels, !dc

Opposite of the above. Leaves the channels and stops listening to commands in them.

# Permissions

### Super admins

Super admins have the right to give other people 'admin' and 'super admin' rights as well as take them away.

They can also make the bot join and leave twitch channels.

### Admins

Admins have the right to give other people the 'user' role and take them away.

They can also add, edit and remove information about a 'player name'.

### Users

Users have the permission to ask the bot for information about a player name.

