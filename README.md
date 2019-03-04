# RangerMountain
Discord Bot That Outputs All Text Into Its Own Channel

**Requires python 3.6**

First time setup:

1. Create your bot on discord.com and add it to the desired servers 
(one instance of this bot running can listen to multiple servers at the same time).
2. Generate bot token
3. Create .token.txt file
```
$ cd /<wherever this is stored>/RangerMountain/
$ echo -n "gEnerATEdTokEnTeXt_123SALSDKJasdjk.fasdfklasdfjALSK" > .token.txt
```
3. Edit bot.py and change OUTPUT_CHANNEL value to new desired channel name:
```
line 16: OUTPUT_CHANNEL = 'theplus'
```

**Now we can run the bot:**

Activate environment:

```
$ source env/bin/activate
```

Run Bot:
```
$ ./bot.py
```

Deactivate environment (when you're done with the bot):

```
$ deactivate
```

**Features:**

Anytime this bot is running, you can type `/help` and send the message in the discord app (on a server it has been added to) to have it show you how you can use it.

The following events are listened to by the bot already:
- on_message
- on_message_delete
- on_message_edit
- on_member_join
- on_member_remove
- on_member_update
- on_channel_create
- on_channel_delete
- on_channel_update
- on_server_join
- on_server_remove
- on_server_update
- on_server_emojis_update
- on_ready

Should you need to add any extra functionality to the bot, visit discord.py to find out how: https://discordpy.readthedocs.io/en/latest/api.html
