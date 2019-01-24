#!/usr/bin/env python3

# Work with Python 3.6
import os
import re
import io
import os
import sys
import discord
import giphypop
import requests
from PIL import Image
from io import BytesIO

STDOUT = sys.stdout
STDERR = sys.stderr
TOKEN = 'NTM0NTczMDY0NTkyMTYyODE5.DyArTA.37TPWbxZarB8fPlsrE042tAKsHY'
OUTPUT_CHANNEL = 'theplus' 

def silence():
    null = open(os.devnull, 'w')
    sys.stdout = null
    sys.stderr = null

def unSilence():
    sys.stdout = STDOUT
    sys.stderr = STDERR

silence()
byteImgIO = io.BytesIO()
giphy = giphypop.Giphy()
bot = discord.Client()
unSilence()

channelDict = {}
commands = {}
theplus = None
lastMessageIsForwarded = {} # { channel.name : message or None if not forwarded }
lastLoggedMessage = None
memberEmojis = {}
messageMap = {} # { originalMessage.id : { 'channelId' : forwardedChannel.id, 'messageId' : forwardedMessage.id, 'attachmentIds' : [forwardedAttachment.id] } }

########################################## Helpers ##########################################

def firstWord(string):
    components = string.split()
    return components[0] if len(components) > 0 else ''

def rest(string):
    components = string.split()
    return ' '.join(components[1:]) if len(components) > 1 else ''

def getForwardedMessageDestination(message):
    return theplus if message.channel != theplus else lastLoggedMessage.channel if lastLoggedMessage else None

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
    elif command == '/at':
        await forward(message)
    elif command == '/meme':
        await meme(message)
    # elif command == '/clear':
    #     if message.channel != theplus:
    #         await sendError(message, '``/clear`` should only be executed from within %s' % theplus.mention)
    #         return

    #     await clear()
    #     await mentionUser(theplus, message.author, '``/clear`` complete! 👌')
            
# async def addOkReaction(message):
#     await bot.add_reaction(message, '👌')

# async def addThinkingReaction(message):
    # await bot.add_reaction(message, '🤔')

########################################## Send Functions ##########################################

async def mentionUser(channel, author, messageString):
    await sendMessage(channel, '%s: %s' % (author.mention, messageString))

async def sendError(message, errorString):
    await sendMessage(message.channel, '%s: %s 🤔' % (message.author.mention, errorString))

# SendAttachment -> Message or None
async def sendAttachment(channel, attachment):
    if not channel or not attachment:
        return None

    url = attachment['url']
    name = attachment['title'] if 'title' in attachment else url.split('/')[-1]
    response = requests.get(url)

    return await bot.send_file(channel, BytesIO(response.content), filename = name)

# SendMessage -> Message or None
async def sendMessage(channel, content):
    if not channel or not content or content == '':
        return None
    
    return await bot.send_message(channel, content)

async def sendQuotedMessage(channel, message):
    global lastMessageIsForwarded, lastLoggedMessage, messageMap

    # Don't send quoted things to same channel
    if not channel or not message or message.channel == channel:
        return

    author = message.author
    name = author.display_name
    emoji = str(memberEmojis[name]) if name in memberEmojis else ':sweat_smile:'
    # header = '%s %s *via* %s [said](https://discordapp.com/channels/%s/%s/%s):\n' % (emoji, name, message.channel.mention, message.server.id, message.channel.id, message.id) if isNewAuthorOrChannel(destinationName = channel.name, message = message) else '' 
    header = '%s %s *via* %s:\n' % (emoji, name, message.channel.mention) if isNewAuthorOrChannel(destinationName = channel.name, message = message) else '' 
    content = '%s%s' % (header, message.content)

    lastMessageIsForwarded[channel.name] = message
    lastLoggedMessage = message if channel == theplus else lastLoggedMessage
    
    forwardedMessage = await sendMessage(channel, content)
    forwardedAttachmentIds = []

    for attachmentDict in message.attachments:
        attachment = await sendAttachment(channel, attachmentDict)

        if attachment:
            forwardedAttachmentIds += [attachment.id]

    if forwardedMessage:
        messageMap[message.id] = {
            'channelId' : channel.id,
            'messageId' : forwardedMessage.id,
            'attachmentIds' : forwardedAttachmentIds
        }

async def editForwardedMessage(message, content):
    return

########################################## Commands ##########################################

async def help(message):
    content = 'This is what I can do for you:\n\n'

    for command, description in commands.items():
        content += '``%s`` : %s\n' % (command, description)

    await mentionUser(message.channel, message.author, content)

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
    
async def meme(message):
    global messageMap
    channel = message.channel
    searchTerms = message.content.strip()

    if not searchTerms or searchTerms == '':
        await sendError(message, '``/meme`` needs at least one search term')
        return

    result = None

    for gif in giphy.search(phrase = searchTerms, limit = 1):
        result = gif

    if not result:
        for gif in giphy.search(term = searchTerms, limit = 1):
            result = gif

    if not result:
        await sendError(message, 'couldn\'t find a relevant meme for *%s*' % searchTerms)
        return    

    attachmentDict = {'url' : result.fixed_height.url, 'title' : '%s.%s' % (result.id, result.type)}
    memeMessage = await sendAttachment(channel, attachmentDict)

    destination = getForwardedMessageDestination(message)
    message.content = '``/meme %s``' % searchTerms
    await sendQuotedMessage(destination, message)
    forwardedMeme = await sendAttachment(destination, attachmentDict)

    messageMap[memeMessage.id] = {
        'channelId' : destination.id,
        'messageId' : forwardedMeme.id,
        'attachmentIds' : []
    }


async def clear():
    async for message in bot.logs_from(theplus):
        await bot.delete_message(message)

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

    try:
        if isACommand(firstWord(content)):
            await execute(firstWord(content), message)
            return
        await sendQuotedMessage(getForwardedMessageDestination(message), message)
    except:
        await sendError(message, '``%s``' % sys.exec_info()[1])

# @bot.event
# async def on_message_edit(before, after):
#     if message.id in messageMap:
#         for forwardedMessage in messageMap[message.id]:
#             editForwardedMessage(forwardedMessage, after.content)

@bot.event
async def on_message_delete(deleted):
    global messageMap

    if deleted.id in messageMap:
        print()
        print('Source message was deleted + forwarded message exists:')
        
        forwarded = messageMap[deleted.id]
        channel = bot.get_channel(forwarded['channelId'])
        message = bot.get_message(channel, forwarded['messageId'])
        attachments = [bot.get_message(channel, attachmentId) for attachmentId in forwarded['attachmentIds']]
        
        try:
            await bot.delete_message(await message)
            print('-> Forwarded message was deleted')
        except:
            print('-> Forwarded message could not be found for deletion')

        try: 
            for attachment in attachments:
                await bot.delete_message(await attachments)
                print('-> Forwarded message\'s attachment was deleted')
        except:
            print('-> Forwarded message\'s attachments could not be found for deletion')
        
        del messageMap[deleted.id]
        print()

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
                '/at'    : 'I\'ll send your message to the channel provided, eg: ``/at #validchannelname text``',   
                '/meme'  : 'I\'ll scour giphy for you and find the most relevant meme, eg: ``/meme some search terms``'
                # /clear is disabled at the moment # '/clear' : 'I\'ll clear every message in %s for you' % theplus.mention
               }
    memberEmojis = { emoji.name : emoji for emoji in bot.get_all_emojis() }

bot.run(TOKEN)
