#!/usr/bin/env python3

# Work with Python 3.6
import discord
import os
import re

TOKEN = 'NTM0NTczMDY0NTkyMTYyODE5.DyArTA.37TPWbxZarB8fPlsrE042tAKsHY'
OUTPUT_CHANNEL = 'theplus' 
COMMANDS = { 
             '/help' : 'Use this to tell you about all the things I can do!', 
             '/echo' : 'I\'ll echo your message back at you with ``/echo text``',
             '/re'   : 'I\'ll send your message to the previous channel! Note: This only works from **#theplus**',
             '/at'   : 'I\'ll send your message to the channel provided, eg: ``/at #validchannelname text``'   
           }

bot = discord.Client()
channelDict = {}
theplus = None
previous = None

#Commands

async def help(message):
    content = 'This is what I can do for you:\n\n'

    for command, description in COMMANDS.items():
        content += '%s : %s\n' % (command, description)

    await sendMessage(message.channel, content)

async def echo(message):
    await sendEmbed(message.channel, message)

async def reply(message):
    global previous
    previousChannel = previous    
    
    if previousChannel == None:
        await sendMessage(message.channel, 'I haven\'t seen any messages from other channels yet!')
        return 

    if message.channel == theplus:
        await sendEmbed(previousChannel, message)
        await addOkReaction(message)
    else:
        await sendMessage(message.channel, '``/re`` doesn\'t work outside of **#theplus**')

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
            await sendMessage(message.channel, '``/at`` should only be used to send messages to other channels')    
    else:
        await sendMessage(message.channel, '``/at`` must be given a valid channel name on this server')
    

#Helpers

def firstWord(string):
    components = string.split()
    return components[0] if len(components) > 0 else ''

def rest(string):
    components = string.split()
    return ' '.join(components[1:]) if len(components) > 1 else ''

def isACommand(string):
    return string in COMMANDS

async def execute(command, message):
    if command not in COMMANDS:
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

async def addOkReaction(message):
    await bot.add_reaction(message, '👌')

#Send functions

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
    global channelDict, theplus

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

bot.run(TOKEN)
