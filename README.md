# WeatherPi
A simple weather forecast display using Raspberry Pi. This program uses Python to query the Weather Underground API for the detailed 36 hour forecast of a user-selected city, then consolidates the results to display temperature and wind forecast information on the Sense HAT accessory for the Raspberry Pi single-board computer.

SETUP

In order for this script to be able to retrieve current weather information, you need to have a Weather Underground API Key. This is a unique sequence of letters and numbers which allows this script to access Weather Underground's forecast information.

Do the following:

1) Get a Weather Underground API Key. In order to get an API key you need to register for one [here](https://www.wunderground.com/weather/api/). The sequence of letters and numbers you receive is your API key, and it is a secret. DO NOT SHARE YOUR API KEY WITH ANYONE.

2) Save your API key to a text file in the same directory as this script named ```APIKey.txt```.

3) Run the script and enter a city and state in the prompt.

4) Move the joystick on the Sense HAT to display the city name and weather information.

Powered by [Weather Underground](www.wunderground.com)
