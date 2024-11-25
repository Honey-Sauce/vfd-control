#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vfd import *
import traceback

def degToCompass(num):
    val=int((num/22.5)+.5)
    arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]

def haDataLoad():
    global ha_data
    try:
        #time.sleep(refreshRate)
        print("Initiating Home Assistant Connection")
        print("Starting Session")
        session = requests.Session()
        print("Adding Token to Header")
        session.headers.update({'Authorization': 'Bearer '+config.haToken})
        print("Getting Home Assistant Sensor Data")
        ha_states = session.get(config.haURL)
        print("Converting Data to Readable Text")
        ha_states.encoding = 'utf-8'
        ha_text = ha_states.text
        print("Loading JSON")
        ha_data = json.loads(ha_text)
        return ha_data
    except:
        print("Failed to get Home Assistant Sensor Data")

def vfdLoop(ha_data):
    line1cycle = 0
    line2cycle = 0
    loops = 0
    timePassed = 0
    line1Prev = ""
    line2Prev = ""        
    lastWeatherCheck = datetime.datetime.now() - datetime.timedelta(minutes=180)
    lastWeatherCheck = lastWeatherCheck.astimezone()
    weatherStartTime = datetime.datetime.strptime(config.startTime, '%H:%M')
    weatherEndTime = datetime.datetime.strptime(config.endTime, '%H:%M')
    conditionDict = {"clear-night": "Clear Night","cloudy": "Cloudy","exceptional": "Exceptional","fog": "Fog","hail": "Hail","lightning": "Lightning","lightning-rainy": "Lightning & Rainy","partlycloudy": "Partly Cloudy","pouring": "Pouring","rainy": "Rainy","snowy": "Snowy","snowy-rainy": "Snowy & Rainy","sunny": "Sunny","windy": "Windy","windy-variant": "Windy"}
    while True: #loop until stopped
        try:
            sleepTime = config.loopDelay
            print(datetime.datetime.now().strftime("------------------ %H:%M:%S.%f"))
            hexList = []
            if config.clockMode == "24h":
                nowTime = datetime.datetime.now().strftime("%H:%M") #get current time
            else:
                nowTime = datetime.datetime.now().strftime("%-I:%M") #get current time
            nowDate = datetime.datetime.now().strftime("%B %d, %Y") #get current date
            #ping = urllib.request.urlopen(config.urlPHP).read() #hit url that generates json data
            elementContent = urllib.request.urlopen(config.urlJSON).read().decode('utf-8') #read remote json file
            elementJSON = json.loads(elementContent) #convert json data to dictionary
            stringText = nowTime #write current time to start of text to be written
            status = None
            for elementKey, elementValue in elementJSON.items():
                for filtered in config.keyFilter:
                    if filtered == elementKey:
                        status = "Playing"
                        line1Text = f"{nowTime}" + f" CHANNEL {elementValue.get('channel')}".center(14, " ")
                        if elementValue.get('category') == "series":
                            if line2cycle == 0:
                                line2Text = elementValue.get('title')
                                line2cycle += 1
                            elif line2cycle == 1:
                                line2Text = f"Season {elementValue['details'].get('season_number')} Episode {elementValue['details'].get('episode_number')} - {elementValue['details'].get('episode_title')}"
                                line2cycle += 1
                            elif line2cycle == 2:
                                line2Text = f"Rated {elementValue.get('rated')}"
                                line2cycle += 1
                            elif line2cycle == 3:
                                line2Text = elementValue.get('plot').split('.')[0]
                                line2cycle = 0
                            else:
                                line2cycle = 0
                        elif elementValue.get('category') == "movie":
                            if line2cycle == 0:
                                line2Text = elementValue.get('title')
                                line2cycle += 1
                            elif line2cycle == 1:
                                line2Text = f"Rated: {elementValue.get('rated').split('/')[0].strip()}"
                                line2cycle += 1
                            elif line2cycle == 2:
                                starring = []
                                while len(starring) < 2:
                                    movie_cast = elementValue['details'].get('cast')
                                    starring.append(movie_cast[len(starring)])
                                line2Text = f"Starring: {movie_cast[0].get('name')} and {movie_cast[1].get('name')}"
                                line2cycle += 1
                            elif line2cycle == 3:
                                line2Text = elementValue.get('tagline')
                                line2cycle = 0
                        elif elementValue.get('category') == "interstitial":
                            line2Text = f"{elementValue.get('title')} ({elementValue['details'].get('year','XX')})"
                        break
                    else:
                        continue
            '''if status == "Playing": #if playing on the defined client
                timePassed = config.refreshRate*1000
                channelDisplay = " CHANNEL " + elementJSON['channelNum'] #add pseudo channel number to first line
                line1Text = nowTime + channelDisplay.center(14, " ") #adjust text positioning
                if elementJSON['mediaType'] == "TV": #if a TV show is playing
                    if line2cycle == 0: #on first rotation display the TV show title
                        line2Text = elementJSON['title']
                        line2cycle = line2cycle + 1
                    elif line2cycle == 1: #on second rotation display the season and episode numbers
                        line2Text = elementJSON['season'] + " Episode " + elementJSON['episodeNum']
                        line2cycle = line2cycle + 1
                    elif line2cycle == 2: #on third rotation display the episode title
                        line2Text = elementJSON['episodeTitle']
                        line2cycle = 0
                elif elementJSON['mediaType'] == "Movie": #if a movie is playing
                    if line2cycle == 0: #on first rotation display the movie title and release year
                        line2Text = elementJSON['title'] + " (" + elementJSON['year'] + ")"
                        line2cycle = line2cycle + 1
                    elif line2cycle == 1: #on second rotation display the movie rating
                        line2Text = "Rated: " + elementJSON['rating']
                        line2cycle = line2cycle + 1
                    elif line2cycle == 2: #on third rotation display actor data
                        line2Text = "Starring: " + elementJSON['actor']
                        line2cycle = line2cycle + 1
                    elif line2cycle == 3: #on fourth rotation display the movie tag line
                        line2Text = elementJSON['tagline']
                        line2cycle = 0
                elif elementJSON['mediaType'] == "Commercial": #if a commercial is playing
                    line2Text = elementJSON['title'] #show the commercial type
                    line2cycle = 1
            elif elementJSON['status'] == "Waiting": #is pseudo channel is on, but nothing is playing
                channelDisplay = " CHANNEL " + elementJSON['channelNum'] #set channel number data
                line1Text = nowTime + channelDisplay.center(14, " ")
                line2Text = "Waiting..." #set line 2 text
                line2Text = '%.20s' % line2Text
                line2cycle = 1'''
            if status is None: #if channel is off and nothing is playing, show the time and date and weather
                if timePassed >= config.refreshRate*1000:
                    ha_data = haDataLoad()
                    loops = 0
                    timePassed = 0
                else:
                    print("Time since last HA data update: " + str(timePassed/1000)+" seconds")
                big_data = ha_data
                for d in big_data:
                    if 'weather' in d:
                        print(json.dumps(d,indent=4))
                    if d['entity_id'] == config.haWeatherEntityID:
                        print(d)
                        try:
                            currentTemp = str(d['attributes']['temperature'])+ "°"
                        except:
                            currentTemp = "XX°"
                        try:
                            currentCondition = str(conditionDict[d['state']])
                        except:
                            currentCondition = str(d['state'])
                        try:
                            currentHumidity = str(d['attributes']['humidity'])+"%"
                        except:
                            currentHumidity = "XX%"
                        try:
                            currentPressure = str(d['attributes']['pressure'])+"mb"
                        except:
                            currentPressure = "Xmb"
                        try:
                            currentWindDir = degToCompass(d['attributes']['wind_bearing'])
                        except:
                            currentWindDir = None
                        try:
                            currentWindSpeed = str(round(d['attributes']['wind_speed']))+" mph"
                        except:
                            currentWindSpeed = "XX mph"
                        '''try:
                            forecastDateTime = datetime.datetime.strptime(d['attributes']['forecast'][0]['datetime'], "%Y-%m-%dT%H:%M:%S%z")
                            forecastTemp_1 = str(d['attributes']['forecast'][0]['temperature'])+ "°"
                            forecastTemp_2 = str(d['attributes']['forecast'][1]['temperature'])+ "°"
                            #forecastTempLow = str(d['attributes']['forecast'][0]['templow'])+"°"
                            forecastCondition = d['attributes']['forecast'][0]['condition']
                            forecastWindDir = degToCompass(d['attributes']['forecast'][0]['wind_bearing'])
                            forecastWindSpeed = str(round(d['attributes']['forecast'][0]['wind_speed']))+" mph"
                            forecastDaytime_1 = d['attributes']['forecast'][0]['is_daytime']
                            forecastDaytime_2 = d['attributes']['forecast'][1]['is_daytime']
                            forecastDetailed_1 = d['attributes']['forecast'][0]['detailed_description']
                            forecastDetailed_2 = d['attributes']['forecast'][1]['detailed_description']
                        except Exception as e:
                            print(e)
                            forecastDateTime = "1970-12-31T00:00:00z"
                            forecastTemp_1 = "XX°"
                            forecastTemp_2 = "XX°"
                            forecastCondition = "ERROR"
                            forecastWindDir = "X"
                            forecastWindSpeed = "X mph"
                            forecastDaytime_1 = True
                            forecastDaytime_2 = True
                            forecastDetailed_1 = "ERROR RECOVERYING FORECAST"
                            forecastDetailed_2 = "ERROR RECOVERING FORECAST"'''
                line1Strings = []
                line2Strings = []
                forecastDetails = ''
                highTemp = None
                lowTemp = None
                line1Strings.append("Now " + currentTemp)
                line2Strings.append("Now: "+currentCondition.capitalize()+" and "+currentTemp)
                line2Strings.append("Now: "+currentHumidity+" Humidity")
                if currentWindDir != None:
                    line2Strings.append("Now: "+currentWindSpeed+" "+currentWindDir+" Wind")
                else:
                    line2Strings.append("Now: "+currentWindSpeed+" Wind")
                timezone = pytz.timezone(config.timezone)
                now_aware = timezone.localize(datetime.datetime.now())
                '''forecastSplit_1 = forecastDetailed_1.split('. ')
                forecastSplit_2 = forecastDetailed_2.split('. ')
                if forecastDaytime_1 == False:
                    line1Strings.append("Low " + forecastTemp_1)
                    line1Strings.append("High " + forecastTemp_2)
                    for splitData in forecastSplit_1:
                        line2Strings.append("Tonight: "+splitData)
                    for splitData in forecastSplit_2:           
                        line2Strings.append("Tomorrow: "+splitData)
                else:
                    line1Strings.append("High " + forecastTemp_1)
                    line1Strings.append("Low " + forecastTemp_2)
                    for splitData in forecastSplit_1:
                        line2Strings.append("Today: "+splitData)
                    for splitData in forecastSplit_2:           
                        line2Strings.append("Tonight: "+splitData)'''
                try:
                    line1Text = nowTime.rjust(5, " ") + line1Strings[line1cycle].rjust(config.charWidth-6, " ")
                except:
                    line1Text = nowTime.rjust(5, " ") + line1Strings[0].rjust(config.charWidth-6, " ")
                if config.showDate == True:
                    line2Text = line2Strings.append(nowDate)
                try:
                    line2Text = line2Strings[line2cycle]
                except:
                    line2Text = line2Strings[0]
                line1cycle = line1cycle + 1
                line2cycle = line2cycle + 1
                if line1cycle >= len(line1Strings):
                    line1cycle = 0
                if line2cycle >= len(line2Strings):
                    line2cycle = 0
                    start = 0
        except Exception as e:
            traceback.print_exc()
            template = "{0}"
            print(template.format(type(e).__name__))
            print(e.args)
            try:
                line1Text = nowTime.rjust(5, " ") + line1Strings[line1cycle].rjust(config.charWidth-6, " ")
            except:
                line1Text = nowTime.rjust(5, " ") + line1Strings[0].rjust(config.charWidth-6, " ")
            line2Text = "EXCEPTION! "+str(e.args)
        line1Text = '%.20s' % line1Text
        #line1Text = line1Text.center(19, " ")
        if line1Text != line1Prev: #check if line 1 is the same as the last loop
            print(line1Text)
            hexPre = "16"
            hexRaw = textToHex(line1Text.upper(),hexPre)
            writeVFD(hexRaw,config.transitionDelay/1000)
            timePassed = timePassed + (len(hexRaw)/2 * config.scrollDelay)
            sleepTime = sleepTime - (len(hexRaw)/2 * config.transitionDelay)
        else: #if line 1 matches what was written to line 1 on the last loop, skip to the next line
            writeVFD("16")
        #line2Text = '%.19s' % line2Text
        if len(line2Text) <= config.charWidth: #if line 2 is less than the display max then display text centered
            line2Text = line2Text.center(config.charWidth, " ")
            if line2Text != line2Prev:
                print(f"{line2Text}",end="\r")
                hexPre = "0A0E"
                hexRaw = textToHex(line2Text.upper(),hexPre)
                writeVFD(hexRaw,config.transitionDelay/1000)
                timePassed = timePassed + (len(hexRaw)/2 * config.scrollDelay)
                sleepTime = sleepTime - (len(hexRaw)/2 * config.transitionDelay)
                
        else: #if line 2 text is more than the display max, scroll text
            minmax = [0,len(line2Text)]
            if line2Text == line2Prev:
                time.sleep(1)
            start = 0
            while start + config.charWidth <= minmax[1]: #scroll text until end of line
                print(f"{line2Text[start:start+config.charWidth]}",end="\r")
                hexPre = "160A0E"
                hexRaw = textToHex(line2Text[start:start+config.charWidth].upper(),hexPre)
                writeVFD(hexRaw,config.scrollDelay/1000)
                timePassed = timePassed + (len(hexRaw)/2 * config.scrollDelay)
                sleepTime = sleepTime - timePassed #reduce sleep time by the amount already slept
                if start == 0: #wait a half second before starting scroll
                    time.sleep(0.5)
                    sleepTime = sleepTime - 500
                    timePassed = timePassed + 500
                start = start + 1
            time.sleep(0.5) #wait time after scroll
            sleepTime = sleepTime - 500
            timePassed = timePassed + 500
        print("")
        if sleepTime < 0: #if sleep time is negative, set to 0
            sleepTime = 0
        time.sleep(sleepTime/1000)
        timePassed = timePassed + sleepTime
        line1Prev = line1Text #set current line 1 to line1Prev to compare on next loop
        line2Prev = line2Text #set current line 2 to line1Prev to compare on next loop
        loops = loops+1

try:
    ha_data = haDataLoad()
    writeVFD('14120E') #reset display (14), carriage return off (12), make cursor invisible (0E)
    vfdLoop(ha_data)
except Exception as e:
    traceback.print_exc()
    template = "{0}"
    print(template.format(type(e).__name__))
    print(e.args)
    writeVFD('14120E') #reset display (14), carriage return off (12), make cursor invisible (0E)
    hexRaw = textToHex("EXCEPTION!","16")
    writeVFD(textToHex(template.format(type(e).__name__)),config.transitionDelay/1000)
    writeVFD("160A0E")
    writeVFD(textToHex(str(e.args)),config.transitionDelay/1000)
    
#vfdLoopThread = Thread ( target=vfdLoop, )
#vfdLoopThread.start()

#haDataThread = Thread( target=haDataLoad, )
#threading.Timer(config.refreshRate, haDataLoad).start()
#haDataThread.join()
#vfdLoopThread.join()
