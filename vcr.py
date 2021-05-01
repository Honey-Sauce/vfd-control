#!/usr/bin/env python
from vfd import *

linecycle = 1
timeloop = "y"
line1Prev = ""
line2Prev = ""        
while timeloop == "y": #loop until stopped
    sleepTime = config.loopDelay
    print(datetime.datetime.now().strftime("------------------ %H:%M:%S.%f"))
    hexList = []
    if config.clockMode == "24h":
        nowTime = datetime.datetime.now().strftime("%H:%M") #get current time
    else:
        nowTime = datetime.datetime.now().strftime("%-I:%M") #get current time
    nowDate = datetime.datetime.now().strftime("%B %d, %Y") #get current date
    ping = urllib.request.urlopen(config.urlPHP).read() #hit url that generates json data
    elementContent = urllib.request.urlopen(config.urlJSON).read().decode('utf-8') #read remote json file
    elementJSON = json.loads(elementContent) #convert json data to dictionary
    stringText = nowTime #write current time to start of text to be written
    if elementJSON['status'] == "Playing": #if plex is playing on the defined client
        channelDisplay = " CHANNEL " + elementJSON['channelNum'] #add pseudo channel number to first line
        line1Text = nowTime + channelDisplay.center(14, " ") #adjust text positioning
        if elementJSON['mediaType'] == "TV": #if a TV show is playing
            if linecycle == 1: #on first rotation display the TV show title
                line2Text = elementJSON['title']
                linecycle = linecycle + 1
            elif linecycle == 2: #on second rotation display the season and episode numbers
                line2Text = elementJSON['season'] + " Episode " + elementJSON['episodeNum']
                linecycle = linecycle + 1
            elif linecycle == 3: #on third rotation display the episode title
                line2Text = elementJSON['episodeTitle']
                linecycle = 1
        elif elementJSON['mediaType'] == "Movie": #if a movie is playing
            if linecycle == 1: #on first rotation display the movie title and release year
                line2Text = elementJSON['title'] + " (" + elementJSON['year'] + ")"
                linecycle = linecycle + 1
            elif linecycle == 2: #on second rotation display the movie rating
                line2Text = "Rated: " + elementJSON['rating']
                linecycle = linecycle + 1
            elif linecycle == 3: #on third rotation display actor data
                line2Text = "Starring: " + elementJSON['actor']
                linecycle = linecycle + 1
            elif linecycle == 4: #on fourth rotation display the movie tag line
                line2Text = elementJSON['tagline']
                linecycle = 1
        elif elementJSON['mediaType'] == "Commercial": #if a commercial is playing
            line2Text = elementJSON['title'] #show the commercial type
            linecycle = 1
    elif elementJSON['status'] == "Waiting": #is pseudo channel is on, but nothing is playing
        channelDisplay = " CHANNEL " + elementJSON['channelNum'] #set channel number data
        line1Text = nowTime + channelDisplay.center(14, " ")
        line2Text = "Waiting..." #set line 2 text
        line2Text = '%.20s' % line2Text
        linecycle = 1
    else: #if pseudo channel is off and nothing is playing, show the time and date
        line1Text = nowTime + "              "
        if config.showDate == True:
            line2Text = nowDate
        else:
            line2Text = "          "
        linecycle = 1
    line1Text = '%.20s' % line1Text
    #line1Text = line1Text.center(19, " ")
    if line1Text != line1Prev: #check if line 1 is the same as the last loop
        print(line1Text)
        hexPre = "16"
        hexRaw = textToHex(line1Text.upper(),hexPre)
        writeVFD(hexRaw,config.transitionDelay/1000)
        sleepTime = sleepTime - (len(hexRaw)/2 * config.transitionDelay)
    else: #if line 1 matches what was written to line 1 on the last loop, skip to the next line
        writeVFD("16")
    #line2Text = '%.19s' % line2Text
    if len(line2Text) <= 20: #if line 2 is less than the display max then display text centered
        line2Text = line2Text.center(20, " ")
        if line2Text != line2Prev:
            print(line2Text,end="\r")
            hexPre = "0A0E"
            hexRaw = textToHex(line2Text.upper(),hexPre)
            writeVFD(hexRaw,config.transitionDelay/1000)
            sleepTime = sleepTime - (len(hexRaw)/2 * config.transitionDelay)
            
    else: #if line 2 text is more than the display max, scroll text
        minmax = [0,len(line2Text)]
        if line2Text != line2Prev:
            start = 0
        while start + config.charWidth <= minmax[1]: #scroll text until end of line
            print(line2Text[start:start+config.charWidth],end="\r")
            hexPre = "160A0E"
            hexRaw = textToHex(line2Text[start:start+config.charWidth].upper(),hexPre)
            writeVFD(hexRaw,config.scrollDelay/1000)
            sleepTime = sleepTime - (len(hexRaw)/2 * config.scrollDelay) #reduce sleep time by the amount already slept
            if start == 0: #wait a half second before starting scroll
                time.sleep(0.5)
                sleepTime = sleepTime - 500
            start = start + 1
        time.sleep(0.5) #wait time after scroll
        sleepTime = sleepTime - 500
    print("")
    if sleepTime < 0: #if sleep time is negative, set to 0
        sleepTime = 0
    time.sleep(sleepTime/1000)
    line1Prev = line1Text #set current line 1 to line1Prev to compare on next loop
    line2Prev = line2Text #set current line 2 to line1Prev to compare on next loop