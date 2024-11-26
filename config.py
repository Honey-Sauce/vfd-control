import configparser

config = configparser.ConfigParser()
config.read('config.ini')
'''for section in config.sections():
    print(f"[{section}]")
    for key, value in config.items(section):
        print(f"{key} = {value}")
    print()  # Blank line between sections'''
## URL and key filter for BEE now playing display
urlJSON = f"{config['BEE'].get('URL')}/live" #URL of generated JSON file
keyFilter = config['BEE'].get('Clients').split(',')

## For Home Assistant API
haToken = config['Home Assistant'].get('Key')
haURL = f"{config['Home Assistant'].get('URL')}/api/states"
haHeaders = {
    "Authorization": haToken,
    "content-type": "application/json"
}
haWeatherEntityID = config['Home Assistant'].get('Weather Entity')
refreshRate = int(config['Home Assistant'].get('Refresh')) #seconds

## Time Window to Show Weather Data (use 24h HH:MM format)
startTime = config['Clock'].get('Weather Start')
endTime = config['Clock'].get('Weather End')

## Display and Refresh Settings
clockMode = config['Clock'].get('Clock Mode') #set clock to 12h or 24h mode
transitionDelay = int(config['VFD'].get('Transition Delay')) #ms delay between letters, set higher for slower transition 
loopDelay = int(config['VFD'].get('Loop Delay')) #ms between data updates
scrollDelay = int(config['VFD'].get('Scroll Delay')) #ms for scroll speed (lower is faster)
if config['Clock'].get('Show Date').lower() == "true" or config['Clock'].get('Show Date').lower() == "yes":
    showDate = True
else:
    showDate = False #whether or not to show the date in the "off" state (True or False)
charWidth = int(config['VFD'].get('Character Width')) #maximum single-line width of display

## VFD Connector to GPIO Settings
pinout = {
    'J1-14':int(config['GPIO'].get('Pin14')), # Reset
    'J1-12':int(config['GPIO'].get('Pin12')), # Ground
    'J1-11':int(config['GPIO'].get('Pin11')), # +5V @ 370mA (TYP)
    'J1-10':int(config['GPIO'].get('Pin10')),# D0 (LSB)
    'J1-9':int(config['GPIO'].get('Pin9')), # D1
    'J1-8':int(config['GPIO'].get('Pin8')), # D2
    'J1-7':int(config['GPIO'].get('Pin7')), # D3
    'J1-6':int(config['GPIO'].get('Pin6')), # D4
    'J1-5':int(config['GPIO'].get('Pin5')), # D5
    'J1-4':int(config['GPIO'].get('Pin4')), # D6
    'J1-3':int(config['GPIO'].get('Pin3')), # D7
    'J1-2':int(config['GPIO'].get('Pin2')),  # Write Strobe
    'J1-1':int(config['GPIO'].get('Pin1'))  # Busy
}

## Character Dictionary
charDict = { #dictionary of characters and corresponding hex values
    " ":'20',
    '!':'21',
    '"':'22',
    '#':'23',
    '$':'24',
    '%':'25',
    '&':'26',
    '\'':'27',
    '(':'28',
    ')':'29',
    '*':'2A',
    '+':'2B',
    ',':'2C',
    '-':'2D',
    '.':'2E',
    '/':'2F',
    '0':'30',
    '1':'31',
    '2':'32',
    '3':'33',
    '4':'34',
    '5':'35',
    '6':'36',
    '7':'37',
    '8':'38',
    '9':'39',
    ':':'3A',
    ';':'3B',
    '<':'3C',
    '=':'3D',
    '>':'3E',
    '?':'3F',
    '@':'40',
    'A':'41',
    'B':'42',
    'C':'43',
    'D':'44',
    'E':'45',
    'F':'46',
    'G':'47',
    'H':'48',
    'I':'49',
    'J':'4A',
    'K':'4B',
    'L':'4C',
    'M':'4D',
    'N':'4E',
    'O':'4F',
    'P':'50',
    'Q':'51',
    'R':'52',
    'S':'53',
    'T':'54',
    'U':'55',
    'V':'56',
    'W':'57',
    'X':'58',
    'Y':'59',
    'Z':'5A',
    '[':'5B',
    '¥':'5C',
    ']':'5D',
    '^':'5E',
    '_':'5F',
    '`':'60',
    'a':'61',
    'b':'62',
    'c':'63',
    'd':'64',
    'e':'65',
    'f':'66',
    'g':'67',
    'h':'68',
    'i':'69',
    'j':'6A',
    'k':'6B',
    'l':'6C',
    'm':'6D',
    'n':'6E',
    'o':'6F',
    'p':'70',
    'q':'71',
    'r':'72',
    's':'73',
    't':'74',
    'u':'75',
    'v':'76',
    'w':'77',
    'x':'78',
    'y':'79',
    'z':'7A',
    '{':'7B',
    '₤':'7C',
    '}':'7D',
    '°':'7E',
    'Ä':'A0',
    'Å':'A1',
    'Á':'A2',
    'Ç':'A3',
    'Â':'A4',
    'Æ':'A5',
    'É':'A6',
    'È':'A7',
    'Ê':'A8',
    'Ï':'A9',
    'Í':'AA',
    'Ì':'AB',
    'Î':'AC',
    'Ö':'AD',
    'Ñ':'AE',
    'Ø':'AF',
    'Ó':'B0',
    'Ò':'B1',
    'À':'B2',
    'ß':'B3',
    'Ë':'B4',
    'Ü':'B5',
    'Ú':'B6',
    'Ù':'B7',
    'Û':'B8',
    '±':'BA',
    '÷':'BB',
    '→':'BC',
    '⇒':'BD',
    '◆':'BE',
    'ä':'C0',
    'å':'C1',
    'á':'C2',
    'ç':'C3',
    'â':'C4',
    'æ':'C5',
    'é':'C6',
    'è':'C7',
    'ê':'C8',
    'ï':'C9',
    'í':'CA',
    'ì':'CB',
    'î':'CC',
    'ö':'CD',
    'ñ':'CE',
    'ø':'CF',
    'ó':'D0',
    'ò':'D1',
    'à':'D2',
    '¢':'D3',
    'ë':'D4',
    'ü':'D5',
    'ú':'D6',
    'ù':'D7',
    'û':'D8',
    '○':'D9',
    '⊙':'DA',
    '●':'DB',
    '▫':'DC',
    '▪':'DD',
    '◇':'DE',
    '⓿':'E0',
    '❶':'E1',
    '❷':'E2',
    '❸':'E3',
    '❹':'E4',
    '❺':'E5',
    '❻':'E6',
    '❼':'E7',
    '❽':'E8',
    '❾':'E9',
    '¡':'80',
    '½':'312F32',
    '⅓':'312F33',
    '¼':'312F34',
    '¾':'332F34',
    '¿':'EA',
    '–':'2D',
    '…':'2E2E2E',
}
