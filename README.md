# RangerMountain
Discord Bot That Outputs All Text Into Its Own Channel

I didn't like how a discord server I was on had many channels and I would always have to switch between them to stay up to date on what's going on, which is very difficult to do when in the middle of playing a game on another screen! I made this bot so that you only have to have a single channel open on a server to be able to follow all the conversations happening there. 

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
4. Edit bot.py and change OUTPUT_CHANNEL value to new desired channel name:
```
line 16: OUTPUT_CHANNEL = 'theplus'
```
5. Make sure OUTPUT_CHANNEL exists on each server this bot will listen to, otherwise you must add a new channel with the exact same name as OUTPUT_CHANNEL to each server through the discord app.

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

**Adding Emojis to your server:**

In the future, I may add functionality to add and manage the emojis automatically, but this only works when the bot has the proper permissions. For now, it has to be done by anyone that has the permissions to do so on their respective discord server.

This bot uses emojis to mimic how discord shows the avatar of whoever sent the message it forwarded. This means there's one more minor step to follow when adding the bot to your server. Whenever the bot is started, or avatars are updated on a discord channel, the bot will grab and update the avatars it knows about. All you have to do is open the settings for each of the servers it runs in, and under the emoji tab, upload the emojis that it saves inside the `.../RangerMountain/avatars` folder. You should also leave the default names of the emojis as the bot named them to mimic the user nicknames. If a user changes their nickname, then update their emoji name accordingly inside the same emoji settings tab. Whenever a user updates their emoji, the user will have to also manually update the emoji by uploading the new avatar image saved in the avatars folder. If there are any users that don't have an emoji, it will use `😅` instead.

**Features:**

Anytime this bot is running, you can type `/help` and send the message in the discord app (on a server it has been added to) to have it show you how you can use it:

- `/help` : Use this to tell you about all the things I can do!
- `/at` : I'll send your message to the channel provided, eg: `/at #validchannelname text`
- `/gif` : I'll scour giphy for you and find the most relevant gif, eg: `/gif some search terms`. If given nothing, then I'll find something at random!
- `/meme` : I'll translate the input into a meme, eg: `/meme some search terms`

Assuming the OUTPUT_CHANNEL exists on each of the servers it's added to, it will forward every message sent on those servers to their
respective OUTPUT_CHANNEL. The bot maintains the normal message formatting that discord already uses, and states which channel the original message was posted. If anyone sends messages from within the OUTPUT_CHANNEL, it will post a reply to the source channel the previous message came from. Otherwise, you can use `/at` to send your message to the right channel if lots of activity keeps changing the last channel that was listened to.

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

Should you need to add any extra functionality to the bot, visit discordpy's site to find out how: https://discordpy.readthedocs.io/en/latest/api.html
