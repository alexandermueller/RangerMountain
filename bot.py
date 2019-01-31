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

# silence()
byteImgIO = io.BytesIO()
giphy = giphypop.Giphy()
bot = discord.Client()
# unSilence()

serverDict = {} # { server.name : { channel.name : channel } }
commands = {}
theplusMap = {} # { server.name : channel }
lastMessageIsForwarded = {} # { server.name : { channel.name : message or None if not forwarded } }
lastLoggedMessage = {} # { server.name : message or None if none logged last }
memberEmojis = {}
messageMap = {} # { originalMessage.id : { 'channelId' : forwardedChannel.id, 'messageId' : forwardedMessage.id, 'attachmentIds' : [forwardedAttachment.id] } }
lastLogWasMessage = False

########################################## Helpers ##########################################

def logEvent(string, isMessage = False):
    global lastLogWasMessage

    if not lastLogWasMessage or lastLogWasMessage != isMessage:
        string = '\n' + string
    
    print(string)
    lastLogWasMessage = isMessage

def firstWord(string):
    components = string.split()
    return components[0] if len(components) > 0 else ''

def rest(string):
    components = string.split()
    return ' '.join(components[1:]) if len(components) > 1 else ''

def getForwardedMessageDestination(message):
    serverName = message.channel.server.name
    return theplusMap[serverName] if message.channel != theplusMap[serverName] else lastLoggedMessage[serverName].channel if serverName in lastLoggedMessage and lastLoggedMessage[serverName] else None

def isACommand(string):
    return string in commands

def isNewAuthorOrChannel(destinationChannel, message):
    channelName = destinationChannel.name
    serverName = destinationChannel.server.name

    return (channelName not in lastMessageIsForwarded[serverName] or 
            not lastMessageIsForwarded[serverName][channelName] or 
            lastMessageIsForwarded[serverName][channelName].author != message.author or
            lastMessageIsForwarded[serverName][channelName].channel != message.channel) 

async def execute(command, message):
    if command not in commands:
        logEvent('-> Error: command "%s" couldn\'t be found.')
        return

    message.content = rest(message.content)
    serverName = message.channel.server.name

    if command == '/help':
        await help(message)
    elif command == '/at':
        await forward(message)
    elif command == '/gif':
        await gif(message)
    elif command == '/meme':
        await meme(message)
            
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

async def sendQuotedMessage(channel, message, cleanContent = True):
    global lastMessageIsForwarded, lastLoggedMessage, messageMap

    # Don't send quoted things to same channel
    if not channel or not message or message.channel == channel:
        return

    serverName = channel.server.name
    author = message.author
    name = author.display_name
    emoji = str(memberEmojis[name]) if name in memberEmojis else ':sweat_smile:'
    header = '%s %s *via* %s:\n' % (emoji, name, message.channel.mention) if isNewAuthorOrChannel(destinationChannel = channel, message = message) else '' # TODO: add [said](https://discordapp.com/channels/%s/%s/%s):\n' % (message.server.id, message.channel.id, message.id)
    content = '%s%s' % (header, message.clean_content if cleanContent else message.content)

    lastMessageIsForwarded[serverName][channel.name] = message
    lastLoggedMessage[serverName] = message if channel == theplusMap[serverName] else lastLoggedMessage[serverName]
    
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
    
async def gif(message):
    global messageMap
    channel = message.channel
    searchTerms = message.content.strip()

    result = None

    if not searchTerms or searchTerms == '':
        searchTerms = ''
        result = giphy.random_gif()
    elif searchTerms != '' :
        for gif in giphy.search(phrase = searchTerms, limit = 1):
            result = gif

        if not result:
            for gif in giphy.search(term = searchTerms, limit = 1):
                result = gif

        if not result:
            await sendError(message, 'couldn\'t find a relevant gif for *%s*' % searchTerms)
            return    

    attachmentDict = {'url' : result.fixed_height.url, 'title' : '%s.%s' % (result.id, result.type)}
    gifMessage = await sendAttachment(channel, attachmentDict)

    destination = getForwardedMessageDestination(message)
    message.content = '``/gif %s``' % (searchTerms if searchTerms != '' else '[%s]' % result.bitly)
    
    await sendQuotedMessage(destination, message, cleanContent = False)
    forwardedGif = await sendAttachment(destination, attachmentDict)

    if not destination:
        return

    messageMap[gifMessage.id] = {
        'channelId' : destination.id,
        'messageId' : forwardedGif.id,
        'attachmentIds' : []
    }

async def meme(message):
    global messageMap
    channel = message.channel
    searchTerms = message.content.strip()

    if not searchTerms or searchTerms == '':
        await sendError(message, '``/meme`` needs at least one search term')
        return

    result = giphy.translate(phrase = searchTerms)

    if not result:
        result = giphy.translate(term = searchTerms)

    if not result:
        await sendError(message, 'couldn\'t find a relevant meme for *%s*' % searchTerms)
        return    

    attachmentDict = {'url' : result.fixed_height.url, 'title' : '%s.%s' % (result.id, result.type)}
    memeMessage = await sendAttachment(channel, attachmentDict)

    destination = getForwardedMessageDestination(message)
    message.content = '``/meme %s``' % searchTerms

    await sendQuotedMessage(destination, message, cleanContent = False)
    forwardedMeme = await sendAttachment(destination, attachmentDict)

    if not destination:
        return

    messageMap[memeMessage.id] = {
        'channelId' : destination.id,
        'messageId' : forwardedMeme.id,
        'attachmentIds' : []
    }

########################################## Events ##########################################        

@bot.event
async def on_message(message):
    global lastMessageIsForwarded

    # we do not want the bot to reply to itself + ignore any messages that don't have a forward channel
    if message.author == bot.user or message.server.name not in theplusMap:
        return

    author = message.author
    channel = message.channel
    server = channel.server
    content = message.content

    lastMessageIsForwarded[server.name][channel.name] = None # Reset because last message on that server's channel wasn't sent by the bot

    logEvent('<"%s"::"#%s">[@%s]: %s' % (message.server.name, message.channel.name, message.author.name, message.clean_content), isMessage = True)

    try:
        if isACommand(firstWord(content)):
            await execute(firstWord(content), message)
            return
        await sendQuotedMessage(getForwardedMessageDestination(message), message)
    except:
        await sendError(message, '``%s``' % sys.exec_info()[1]) # TODO: this is most likely useless, make it less so

@bot.event
async def on_message_delete(deleted):
    global messageMap

    if deleted.id in messageMap:
        string = '-> Source message was deleted + forwarded message exists:'
        forwarded = messageMap[deleted.id]
        channel = bot.get_channel(forwarded['channelId'])
        message = bot.get_message(channel, forwarded['messageId'])
        attachments = [bot.get_message(channel, attachmentId) for attachmentId in forwarded['attachmentIds']]
        
        try:
            await bot.delete_message(await message)
            string += '\n->\tForwarded message was deleted'
        except:
            string += '\n->\tForwarded message could not be found for deletion'

        try: 
            for attachment in attachments:
                await bot.delete_message(await attachments)
                string += '\n->\tForwarded message\'s attachment was deleted'
        except:
            string += '\n->\tForwarded message\'s attachments could not be found for deletion'
        
        del messageMap[deleted.id]
        logEvent(string)

@bot.event
async def on_message_edit(before, after):
    global messageMap

    if before.id in messageMap:
        string = '-> Source message was edited + forwarded message exists:'
        
        forwarded = messageMap[before.id]
        channel = bot.get_channel(forwarded['channelId'])
        message = bot.get_message(channel, forwarded['messageId'])
        
        try:
            await bot.edit_message(await message, new_content = after.clean_content) 
            string += '\n->\tForwarded message was edited'
        except:
            string += '\n->\tForwarded message could not be found for editing'

        logEvent(string)

@bot.event
async def on_channel_create(channel):
    logEvent('-> Channel "%s" was created on server "%s".' % (channel.name, channel.server.name))
    updateServerMappings()

@bot.event
async def on_channel_delete(channel):
    logEvent('-> Channel "%s" was created on server "%s".' % (channel.name, channel.server.name))
    updateServerMappings()

@bot.event
async def on_channel_update(before, after):
    string = '-> Channel "%s" was updated on server "%s".' % (before.name, before.server.name)
    
    if before.name != after.name:
        string += '\n->\tChannel "%s" is now "%s" on server "%s".' % (before.name, after.name, before.server.name)

    logEvent(string)
    updateServerMappings()

@bot.event
async def on_server_join(server):
    logEvent('-> Server "%s" was joined.' % server.name)
    updateServerMappings()

@bot.event
async def on_server_remove(server):
    logEvent('-> Server "%s" was removed.' % server.name)
    updateServerMappings()

@bot.event
async def on_server_update(before, after):
    string = '-> Server "%s" was updated.' % before.name

    if before.name != after.name:
        string += '\n->\tServer "%s" is now "%s".' % (before.name, after.name)

    logEvent(string)
    updateServerMappings()

@bot.event
async def on_server_emojis_update(before, after):
    logEvent('-> The available emojis were updated.')
    initializeEmojis()

@bot.event
async def on_ready():
    logEvent('-> Logged in as "%s" - %s' % (bot.user.name, bot.user.id))
    initializeCommands()
    initializeEmojis()
    updateServerMappings()

########################################## Initialize Functions ##########################################        

def updateServerMappings():
    global serverDict, theplusMap, lastMessageIsForwarded
    string = '-> Updating Server Mappings:'

    for server in bot.servers:
        if server.name not in serverDict:
            serverDict[server.name] = {}
            lastMessageIsForwarded[server.name] = {}

        for channel in server.channels:
            if channel.name not in serverDict[server.name]:
                serverDict[server.name][channel.name] = channel
                lastMessageIsForwarded[server.name][channel.name] = None

    for serverName, serverChannelDict in serverDict.items():
        if OUTPUT_CHANNEL not in serverChannelDict:
            string += '\n->\tError: Channel "%s" couldn\'t be found in "%s".' % (OUTPUT_CHANNEL, serverName)
            string += '\n->\tThe following channels were found:'

            for channelName, channels in serverChannelDict.items():
                string += '\n->\t - "%s" : "%s"' % (serverName, channelName)
            
            string += '\n->\tNot including server "%s" when listening for events.' % serverName
            continue

        theplusMap[serverName] = serverChannelDict[OUTPUT_CHANNEL]
        lastLoggedMessage[serverName] = None

    if len(theplusMap) == 0:
        string += '\n->\tError: Channel "%s" couldn\'t be found in any of the servers this bot is a member of.' % OUTPUT_CHANNEL
    else:
        string += '\n->\tServer mappings updated successfully.'

    logEvent(string)

def initializeCommands():
    global commands
    commands = { 
                '/help' : 'Use this to tell you about all the things I can do!', 
                '/at'   : 'I\'ll send your message to the channel provided, eg: ``/at #validchannelname text``',   
                '/gif'  : 'I\'ll scour giphy for you and find the most relevant gif, eg: ``/gif some search terms``. If given nothing, then I\'ll find something at random!',
                '/meme' : 'I\'ll translate the input into a meme, eg: ``/meme some search terms``'
               }

def initializeEmojis():
    global memberEmojis
    memberEmojis = { emoji.name : emoji for emoji in bot.get_all_emojis() } # This probably breaks if there are members/emojis in different channels with the same name...?

########################################## Run Bot ##########################################        

bot.run(TOKEN)
