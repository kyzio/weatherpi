############################################################################
#This script utilizes the Weather Underground API to pull weather forecast #
#information for a selected city and display that information on the       #
#Raspberry Pi Sense Hat accessory board. Powered by Weather Underground    #
#(www.wunderground.com).                                                   #
#                                                                          #
############################################################################

#TO CONFIGURE
#1. Register for an API key on wunderground.com.
#2. Save that API key to a text file titled "APIKey.txt" in the same directory as this script
#3. Run the program
#4. Use the Sense Hat joystick to select weather information

#TODO LIST
#1. Implement multiple city forecast selection
#2. Implement a configuration file so user can select and save cities one time, then use the device
#   without needing to edit any code or have a monitor.
#3. Add handling of error responses from Wunderground (ex. if user enters a non-existent city).

#NOTES
# - This script does not work on Windows without commenting out the Raspberry Pi Sense Hat specific calls.
# - This script does not implement controls on user input, and is thereby vulnerable to API key abuse
#   by non-trusted parties. THIS SCRIPT IS NOT SECURE.

##MODULES

import json
import requests
import time
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED

##FUNCTIONS

#returns weather information when called. Supports optional parameter to retrieve current conditions.
def queryWeather(forecastType = None):

    if forecastType == 'current':
        i = '/geolookup/conditions/q/'
    #capability to pull current weather only. Not used.
    else:
        i = '/hourly/q/'
    j = state + '/' + city + '.json'
    #get the Wunderground API key from the APIKey.txt file in the same directory as this script
    with open("APIKey.txt") as apiKey:
        k = apiKey.read()
    l = requests.get('http://api.wunderground.com/api/' + k + '/' + i + j)
    return l

#format the original user input of the city name for use in the program
def formatCity(city):
    i = city.title()
    j = i.strip()
    return j

#format the city string which results from the formatCity function to the format needed for the filename
def cityFileName(city):
    i = "".join(city.split())
    j = i.replace(",","")
    return j

#ensure the two letter state abreviation is in all caps
def formatState(state):
    i = state.upper()
    j = i.strip()
    return j

#retrieve the last weather data .txt file of the query results if it exists
def getLastData(fileName):
    #open text file created by WeatherPi.py
    #with open(file + '.txt', 'w') as weatherData:
    i = (fileName + '.txt')
    with open(i) as weatherData:
        #read the contents of the weather data file into a str
        j = weatherData.read()
        k = json.loads(j)
        print("Prior data found and loaded.")
    return k

#pull the forecast date from the WUnderground query response
def getDataDate(JSONData):
    #get the run date and time of the query
    prettyDate = JSONData['hourly_forecast'][0]['FCTTIME']['pretty']
    #load the report date into a datetime object
    print('The forecast data for ' + cityState + ' starts at ' + prettyDate)

    try:
        date = JSONData['hourly_forecast'][0]['FCTTIME']['epoch']
    except:
        print("ERROR: Unable to locate forecast date in forecast data.")
    return date

def updateData(data):
    #find time of last query run from stored JSON data
    #if there is no stored JSON file, this will throw an error
    try:
        dataDate = getDataDate(data)
    except:
        print('No valid prior data found for ' + cityState + '.')
        dataDate = 0
    #if weather data is more than one hour old, query the Wunderground API
    #the time in the forecast date is always the nearest hour in the future
    if time.time() < int(dataDate):
        print ('The saved weather data for ' + cityState + ' is current.')
        return data
    else:
        print ('Weather data for ' + cityState + ' is out of date.')
        i = queryWeather().text
        j = json.loads(i)
        print ('Weather data updated.')
        #use open functionality to create a txt file of the query results
        outfile = open(fileName + '.txt', 'w')
        k = json.dumps(j,indent=4)
        outfile.write(k)
        outfile.close()
        return j

#loads the forecasted temperature by hour into an ordered list
def valueList(JSONData,fType):
    hoursAhead = 0
    forecastPrefix = JSONData['hourly_forecast']
    valueList = []
    
    while hoursAhead < 36:

        if fType == "temp":
            val = int(forecastPrefix[hoursAhead]['temp']['english'])

        if fType == "wind":
            val = int(forecastPrefix[hoursAhead]['wspd']['english'])

        valueList.append(val)
        hoursAhead += 1
    return valueList

#returns an ordered list which of the weather data which is cut to fit the Sense Hat display
def ledList(valueList,divNum):
    ledList = []
    i = 0

    #take first sixteen values, select every second starting with zero, scale according to the divisor
    #provided in the function call, then round it to a single digit.
    while i < 16:
        val =(valueList[i])
        val = round(int(val)/divNum)
        ledList.append(val)
        i += 2
    return ledList

#function that loads new 64 item array representing lit pixels
def displayPix(ledList,color):

    row = 0
    column = 0
    litPixels = 0
    display = []

    #display colors
    #black
    X = [255, 255, 255]
    
    #represents each row top to bottom
    while row < 8:
        #represents each column within the current row
        while column < 8:
            if litPixels < ledList[row]:
                display.append(color)
                litPixels += 1
            else:
                display.append(X)
                litPixels += 1
            column += 1
        row += 1
        column = 0
        litPixels = 0
        rowPixel = 0
    #shows the display in RGB values for testing purposes
    #print (display)
    return display

#makes sure weather data is current and readies data for display on the Sense Hat
def doData():
    global data
    #make sure data being used is up to date
    data = updateData(data)

    #retrieve temperature data from the JSON file and put it into a list
    vList = valueList(data,"temp")
    #formats temp list of values to fit on the Sense HAT display
    lList = ledList(vList,10)
    #loads the list into a 64 item list to fill the Sense HAT display
    display = (displayPix(lList,[0,255,0]))
    dList.append(display)

    #retrieve wind data from the JSON file and put it into a list
    vList = valueList(data,"wind")
    #formats the list of values to fit on the Sense HAT display
    lList2 = ledList(vList,5)
    #loads the list into a 64 item list to fill the Sense HAT display
    display2 = (displayPix(lList2,[0,0,255]))
    dList.append(display2)

#JOYSTICK FUNCTIONS
def clamp(value, minValue = 0, maxValue = 1):
    return min(maxValue,max(value,minValue))

def joyL(event):
    global displayNumber
    if event.action != ACTION_RELEASED:
        displayNumber = clamp(displayNumber - 1)
        refresh(event)

def joyR(event):
    global displayNumber
    if event.action != ACTION_RELEASED:
        displayNumber = clamp(displayNumber + 1)
        refresh(event)

def joyU(event):
    global cityNumber
    if event.action != ACTION_RELEASED:
        sense.show_message(userInput,scroll_speed=0.04)

def joyD(event):
    global cityNumber
    if event.action != ACTION_RELEASED:
        sense.show_message(userInput,scroll_speed=0.04)

def refresh(event):
    global displayNumber
    if event.action != ACTION_RELEASED:
        doData()
        sense.clear()
        if displayNumber == 0:
            sense.show_message("Temp",scroll_speed=0.04)
        if displayNumber == 1:
            sense.show_message("Wind",scroll_speed=0.04)
        sense.set_rotation(90)
        sense.set_pixels(dList[displayNumber])
        time.sleep(5)
        sense.clear()
        sense.set_rotation(180)

##PROGRAM

#get city on which to check weather
while True:
    userInput = str(input("Please enter a city and state in the format: City, ST \n"))
    if userInput:
        break
    print('You must enter a city and state.')
    
#split up the user input into city and state values
userComma = userInput.find(',')
userCity = (userInput[:userComma])
userState = (userInput[userComma + 1:]) 

#make the user input pretty
city = formatCity(userCity)
state = formatState(userState)
cityState = str(city + ', ' + state)
fileName = cityFileName(cityState)

#display variables to track the different graphs for display on the Sense Hat
#the current display number which will be shown on the Sense Hat
displayNumber = 0
#list of pixels for the first data display (temperature)
display = []
#list of pixels for the second data display (wind)
display2 = []
#list of the data displays to enable switching between displays. A list of lists.
dList = []

#see if there is any prior data and retrieve it if available
try:
    data = getLastData(fileName)
except:
    data = ''

doData()

##RASPBERRY PI SENSE HAT SETUP
sense = SenseHat()
sense.set_rotation(180)
sense.low_light = True
    
#sense.stick.direction attributes are always on the lookout. No need for loops.
sense.stick.direction_left = joyL
sense.stick.direction_right = joyR
sense.stick.direction_up = joyU
sense.stick.direction_down = joyD






