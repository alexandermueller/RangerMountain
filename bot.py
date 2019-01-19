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
lastMessageIsForwarded = {} #{ channel.name : message or None if not forwarded }
lastLoggedMessage = None
memberEmojis = {}

########################################## Commands ##########################################

async def help(message):
    content = 'This is what I can do for you:\n\n'

    for command, description in commands.items():
        content += '``%s`` : %s\n' % (command, description)

    await mentionUser(message.channel, message.author, content)

async def reply(message):    
    if message.channel != theplus:
        await sendError(message, '``/re`` doesn\'t work outside of %s' % theplus.mention)
        return

    if lastLoggedMessage == None:
        await sendError(message, 'I haven\'t seen any messages from other channels yet!')
        return
    
    destination = lastLoggedMessage.channel
    await sendQuotedMessage(destination, message)
    await addOkReaction(message)

async def forward(message):
    channelRepresentation = firstWord(message.content)
    match = re.match(r'\<\#(\d+)\>', channelRepresentation)
    
    if not match:
        await sendError(message, '``/at`` must be given a valid channel name on this server')
        return

    channelId = match.group(0)[2:-1]
    channel = bot.get_channel(channelId)
    message.content = rest(message.content)

    if channel == message.channel:
        await sendError(message, '``/at`` should only be used to send messages to other channels')
        return

    await sendQuotedMessage(channel, message)
    await addOkReaction(message)            
    
async def clear():
    async for message in bot.logs_from(theplus):
        await bot.delete_message(message)

########################################## Helpers ##########################################

def firstWord(string):
    components = string.split()
    return components[0] if len(components) > 0 else ''

def rest(string):
    components = string.split()
    return ' '.join(components[1:]) if len(components) > 1 else ''

def isACommand(string):
    return string in commands

def isNewAuthorOrChannel(destinationName, message):
    return (destinationName not in lastMessageIsForwarded or 
            not lastMessageIsForwarded[destinationName] or 
            lastMessageIsForwarded[destinationName].author != message.author or
            lastMessageIsForwarded[destinationName].channel != message.channel) 

async def execute(command, message):
    if command not in commands:
        print('Error: command "%s" couldn\'t be found.')
        return

    message.content = rest(message.content)

    if command == '/help':
        await help(message)
    elif command == '/re':
        await reply(message)
    elif command == '/at':
        await forward(message)
    elif command == '/clear':
        if message.channel != theplus:
            await sendError(message, '``/clear`` should only be executed from within %s' % theplus.mention)
            return

        await clear()
        await mentionUser(theplus, message.author, '``/clear`` complete! 👌')
            
async def addOkReaction(message):
    await bot.add_reaction(message, '👌')

# async def addThinkingReaction(message):
    # await bot.add_reaction(message, '🤔')

########################################## Send Functions ##########################################

async def mentionUser(channel, author, messageString):
    await sendMessage(channel, '%s: %s' % (author.mention, messageString))

async def sendError(message, errorString):
    await sendMessage(message.channel, '%s: %s 🤔' % (message.author.mention, errorString))

async def sendAttachment(channel, attachment):
    await bot.send_message(channel, attachment['url'])

async def sendMessage(channel, content):
    if content and content != '':
        await bot.send_message(channel, content)

async def sendQuotedMessage(channel, message):
    global lastMessageIsForwarded, lastLoggedMessage

    # Don't send quoted things to same channel
    if message.channel == channel:
        return

    author = message.author
    name = author.display_name
    emoji = str(memberEmojis[name]) if name in memberEmojis else ':sweat_smile:'
    header = '%s %s *via* %s:\n' % (emoji, name, message.channel.mention) if isNewAuthorOrChannel(destinationName = channel.name, message = message) else '' 
    content = '%s%s' % (header, message.content)

    lastMessageIsForwarded[channel.name] = message
    lastLoggedMessage = message if channel == theplus else lastLoggedMessage
    
    await sendMessage(channel, content)
    
    for attachment in message.attachments:
        await sendAttachment(channel, attachment)

########################################## Events ##########################################        
        
@bot.event
async def on_message(message):
    global lastMessageIsForwarded

    # we do not want the bot to reply to itself
    if message.author == bot.user or theplus == None:
        return

    author = message.author
    channel = message.channel
    content = message.content
    lastMessageIsForwarded[channel.name] = None # Reset because last message on that channel wasn't sent by the bot

    if isACommand(firstWord(content)):
        await execute(firstWord(content), message)
        return

    await sendQuotedMessage(theplus, message)

@bot.event
async def on_ready():
    global channelDict, theplus, commands, memberEmojis

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
    
    theplus = channelDict[OUTPUT_CHANNEL]
    commands = { 
                '/help'  : 'Use this to tell you about all the things I can do!', 
                '/re'    : 'I\'ll send your message to the previous channel! Note: this only works from %s' % theplus.mention,
                '/at'    : 'I\'ll send your message to the channel provided, eg: ``/at #validchannelname text``',   
                # /clear is disabled at the moment # '/clear' : 'I\'ll clear every message in %s for you' % theplus.mention
               }
    memberEmojis = { emoji.name : emoji for emoji in bot.get_all_emojis() }

bot.run(TOKEN)
