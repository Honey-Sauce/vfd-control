#!/usr/bin/env python
import sys
import datetime
import time
import pytz
import json
import math
import RPi.GPIO as GPIO
import urllib.request
import config
import requests
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
strArg = sys.argv

## Set pins to send data
GPIO.setup(config.pinout['J1-10'], GPIO.OUT)
GPIO.setup(config.pinout['J1-9'], GPIO.OUT)
GPIO.setup(config.pinout['J1-8'], GPIO.OUT)
GPIO.setup(config.pinout['J1-7'], GPIO.OUT)
GPIO.setup(config.pinout['J1-6'], GPIO.OUT)
GPIO.setup(config.pinout['J1-5'], GPIO.OUT)
GPIO.setup(config.pinout['J1-4'], GPIO.OUT)
GPIO.setup(config.pinout['J1-3'], GPIO.OUT)
GPIO.setup(config.pinout['J1-2'], GPIO.OUT)

## Function to send hex digits over GPIO to the VFD unit
def writeVFD(hexRaw,sleep=0):
    # Place a comma between each hex digit and split into a list array
    hexList = ','.join(hexRaw[i:i+2] for i in range(0, len(hexRaw), 2))
    hexList = hexList.split(',')
    # Send each digit over GPIO
    for hexInput in hexList:
        # Convert hex to binary
        end_length = len(hexInput)*4
        hexInt = int(hexInput, 16)
        hexBin = bin(hexInt)[2:].zfill(end_length)
        # Set VFD Write Strobe to 0
        GPIO.output(config.pinout['J1-2'],0)
        # Set each GPIO pin to 1 bit of the binary value
        GPIO.output(config.pinout['J1-3'],int(hexBin[0])) #D7
        GPIO.output(config.pinout['J1-4'],int(hexBin[1])) #D6
        GPIO.output(config.pinout['J1-5'],int(hexBin[2])) #D5
        GPIO.output(config.pinout['J1-6'],int(hexBin[3])) #D4
        GPIO.output(config.pinout['J1-7'],int(hexBin[4])) #D3
        GPIO.output(config.pinout['J1-8'],int(hexBin[5])) #D2
        GPIO.output(config.pinout['J1-9'],int(hexBin[6])) #D1
        GPIO.output(config.pinout['J1-10'],int(hexBin[7])) #D0
        # Set VPD Write Strobe to 1
        GPIO.output(config.pinout['J1-2'],1)
        # Wait for defined amount of time before writing the next character
        time.sleep(sleep)

def cursorBack(): # Cursor Back One Space
    writeVFD('08')

def cursorForward(): # Cursor Forward One Space
    writeVFD('09')

def cursorDown(): # Cursor Forward Down to bottom line
    writeVFD('0A')

def carriageReturn(): # Returns to left-most character of the same line
    writeVFD('0A')

def cursorHide(): # Make Cursor Invisible
    writeVFD('0E')

def cursorUnhide(): # Make Cursor Visible
    writeVFD('0F')
    
def resetDisplay(): # Reset VFD Unit
    writeVFD('14')
    
def displayClear(): # Clear VFD Unit
    writeVFD('15')

def cursorHome(): # Return Cursor to upper left position
    writeVFD('16')

def cursorPos(position): # Move Cursor to Position
    writeVFD('1B'+position)

## Function to convert text to the corresponding hex values as defined in the character dictionary in the config file
def textToHex(stringText,hexRaw=""):
    for character in stringText:
        try:
            hexRaw = hexRaw + config.charDict[character]
        except KeyError:
            hexRaw = hexRaw + "3F"
    return hexRaw

writeVFD('14120E') #reset display (14), carriage return off (12), make cursor invisible (0E)
r = 0
rawText = ""
stringText = ""
for string in strArg: #if argument exists, set text to be written to the argument value
    if r != 0:
        stringText = str(rawText) + " " + str(string)
    r = r+1
hexPre = "0E15"
if stringText != "": #if there is argument text, write it to display
    if strArg[1] == "--shutdown":
        writeVFD('14120E') #reset display (14), carriage return off (12), make cursor invisible (0E)
        line1 = "SHUTTING"
        line2 = "DOWN"
        hexRaw = textToHex(line1.center(20),hexPre)
        writeVFD(hexRaw,int(config.transitionDelay)/1000)
        hexRaw = textToHex(line2.center(20),"160A")
        writeVFD(hexRaw,int(config.transitionDelay)/1000)
        time.sleep(2)
        writeVFD('14120E') #reset display (14), carriage return off (12), make cursor invisible (0E)
    else:
        hexRaw = textToHex(stringText,hexPre)
        writeVFD(hexRaw,int(config.transitionDelay)/1000)
elif stringText == "": #if there is no argument, do this instead
    hexRaw = textToHex("INITIALIZING",hexPre)
    writeVFD(hexRaw,int(config.transitionDelay)/1000)
    hexRaw = textToHex("DISPLAY","160A")
    writeVFD(hexRaw,int(config.transitionDelay)/1000)
time.sleep(1)
#writeVFD('14120E') #reset display (14), carriage return off (12), make cursor invisible (0E)