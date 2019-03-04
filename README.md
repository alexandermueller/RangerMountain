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
```line 16: OUTPUT_CHANNEL = 'theplus'```

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
