#!/usr/bin/env python3

# Work with Python 3.6
import discord
import os
import re

TOKEN = 'NTM0NTczMDY0NTkyMTYyODE5.DyArTA.37TPWbxZarB8fPlsrE042tAKsHY'
OUTPUT_CHANNEL = 'theplus' 

bot = discord.Client()
channelDict = {}
commands = {}
theplus = None
previous = None

# Commands #

async def help(message):
    content = 'This is what I can do for you:\n\n'

    for command, description in commands.items():
        content += '``%s`` : %s\n' % (command, description)

    await mentionUser(message.channel, message.author, content)

async def echo(message):
    await sendEmbed(message.channel, message)

async def reply(message):
    global previous, theplus
    previousChannel = previous    
    
    if previousChannel == None:
        await sendError(message, 'I haven\'t seen any messages from other channels yet!')
        return 

    if message.channel == theplus:
        await sendEmbed(previousChannel, message)
        await addOkReaction(message)
    else:
        await sendError(message, '``/re`` doesn\'t work outside of %s' % theplus.mention)

async def forward(message):
    channelRepresentation = firstWord(message.content)
    match = re.match(r'\<\#(\d+)\>', channelRepresentation)
    
    if match:
        channelId = match.group(0)[2:-1]
        channel = bot.get_channel(channelId)
        message.content = rest(message.content)

        if channel != message.channel: 
            await sendEmbed(channel, message)
            await addOkReaction(message)
        else:
            await sendError(message, '``/at`` should only be used to send messages to other channels')
    else:
        await sendError(message, '``/at`` must be given a valid channel name on this server')
    
async def clear():
    async for message in bot.logs_from(theplus):
        await bot.delete_message(message)

# Helpers #

def firstWord(string):
    components = string.split()
    return components[0] if len(components) > 0 else ''

def rest(string):
    components = string.split()
    return ' '.join(components[1:]) if len(components) > 1 else ''

def isACommand(string):
    return string in commands

async def execute(command, message):
    if command not in commands:
        print('Error: command "%s" couldn\'t be found.')
        return

    message.content = rest(message.content)

    if command == '/help':
        await help(message)
    elif command == '/echo':
        await echo(message)
    elif command == '/re':
        await reply(message)
    elif command == '/at':
        await forward(message)
    elif command == '/clear':
        if message.channel == theplus:
            await clear()
            await mentionUser(theplus, message.author, '``/clear`` complete! 👌')
        else:
            await sendError(message, '``/clear`` should only be executed from within %s' % theplus.mention)

async def addOkReaction(message):
    await bot.add_reaction(message, '👌')

# async def addThinkingReaction(message):
    # await bot.add_reaction(message, '🤔')

# Send Functions #

async def mentionUser(channel, author, messageString):
    await sendMessage(channel, '%s: %s' % (author.mention, messageString))

async def sendError(message, errorString):
    await sendMessage(message.channel, '%s: %s 🤔' % (message.author.mention, errorString))

async def sendAttachment(channel, attachment):
    await bot.send_message(channel, attachment['url'])

async def sendMessage(channel, content):
    await bot.send_message(channel, content)

async def sendEmbed(channel, message):
    author = message.author
    content = message.content

    embed = discord.Embed()
    embed.set_author(name = '%s @%s:' % (author.nick, message.channel.name), icon_url = author.avatar_url)

    await bot.send_message(channel, embed = embed)

    if len(content) > 0:
        await sendMessage(channel, content)
    
    for attachment in message.attachments:
        await sendAttachment(channel, attachment)

# Events #        
        
@bot.event
async def on_message(message):
    global previous

    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    author = message.author
    channel = message.channel
    content = message.content

    if theplus != None and (channel != theplus or isACommand(firstWord(content))):
        if isACommand(firstWord(content)):
            await execute(firstWord(content), message)
        else:
            previous = channel
            await sendEmbed(theplus, message)

@bot.event
async def on_ready():
    global channelDict, theplus, commands

    print()
    print('Logged in as "%s" - %s ' % (bot.user.name, bot.user.id))

    channels = bot.get_all_channels()
    channelDict = { channel.name : channel for channel in channels }

    if OUTPUT_CHANNEL not in channelDict:
        print()
        print('Error: Channel "%s" couldn\'t be found.' % OUTPUT_CHANNEL)
        print('The following channels were found:')

        for name, channel in channelDict.items():
            print(' - \"%s\"' % name)
        print()

        bot.close()
        os._exit(0)
    else:
        theplus = channelDict[OUTPUT_CHANNEL]
        commands = { 
                    '/help'  : 'Use this to tell you about all the things I can do!', 
                    '/echo'  : 'I\'ll echo your message back at you with ``/echo text``',
                    '/re'    : 'I\'ll send your message to the previous channel! Note: This only works from %s' % theplus.mention,
                    '/at'    : 'I\'ll send your message to the channel provided, eg: ``/at #validchannelname text``',   
                    '/clear' : 'I\'ll clear every message in %s for you' % theplus.mention
                   }

bot.run(TOKEN)
