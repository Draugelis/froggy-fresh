import os
import requests
import json
import hikari
import lightbulb
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from geopy.geocoders import Nominatim


weather_plugin 	= lightbulb.Plugin("Weather")

class Weather:
	"""Weather class that interacts with OpenWeatherMap API
	for weather information
	"""	
	def __init__(self):		
		load_dotenv(dotenv_path=find_dotenv(usecwd=True))
		self._weather_token = os.environ.get('WEATHER_TOKEN')
		self.name = os.environ.get('BOT_NAME')
		self.location = os.environ.get('DEFAULT_LOCATION')

	def t_convert(self, t, time_format = "%m/%d %H:%M"):
		"""Converting UNIX time to human readable time

		Args:
			t (int): UNIX timestamp
			time_format (str, optional): Date format. Defaults to "%m/%d %H:%M".

		Returns:
			str: Human readable time
		"""		
		return datetime.utcfromtimestamp(t).strftime(time_format)

	def get_weather(self, location, exclude):
		"""Get weather for a given location using OpenWeatherMap OneCall API
		API reference: https://openweathermap.org/api/one-call-api

		Args:
			location (string): Target location (e.g. London, New York, Paris)
			exclude (string): Fields to exclude from OneCall API response

		Returns:
			dict: OneCall API response dictionary
		"""		
		self.endpoint = "https://api.openweathermap.org/data/2.5/onecall"
		self.headers = {
			"user-agent": self.name
		}

		self.geolocator = Nominatim(user_agent = self.name)
		self.latitude = self.geolocator.geocode(location).latitude
		self.longitude = self.geolocator.geocode(location).longitude

		self.params = {
			"lat" : self.latitude,
			"lon" : self.longitude,
			"exclude" : exclude,
			"appid"	: self._weather_token
		}

		self.response = requests.request("POST", self.endpoint, params = self.params, headers = self.headers)
		self.data = json.loads(self.response.text)

		return self.data

	def get_city_name(self, location):
		"""Generate location name in `{City}, {Country}` format.
		For example: London, United Kingdom

		Args:
			location (str): Target location

		Returns:
			str: Location name in `{City}, {Country}`
		"""		
		# Example geolocation value
		# Location(London, Greater London, England, United Kingdom, (51.5073219, -0.1276474, 0.0))
		self.geolocator = Nominatim(user_agent = self.name)
		self.geolocation = self.geolocator.geocode(location, language = "en-us")
		self.city = self.geolocation[0].split(", ")[0]
		self.country = self.geolocation[0].split(", ")[-1]

		return f"{self.city}, {self.country}"


	def get_current(self, location):
		"""Get current weather for a given location

		Args:
			location (str): Target location

		Returns:
			dict: dict with the current weather data 
		"""		
		self.exclude = "minutely,hourly,daily",
		self.data = self.get_weather(location, self.exclude)
		
		self.icon = self.data["current"]["weather"][0]["icon"]
		self.icon_url = f"http://openweathermap.org/img/wn/{self.icon}@2x.png"

		# Celsius = Kelvin - 273.15
		self.current_temp 		= self.data["current"]["temp"] - 273.15
		self.feels_like 		= self.data["current"]["feels_like"] - 273.15

		self.current_data = {
			"location" : self.get_city_name(location),
			"current_temp" : self.current_temp,
			"feels_like" : self.feels_like,
			"icon_url" : self.icon_url,
		}

		return self.current_data


@weather_plugin.command
@lightbulb.option("location", "Location for current weather", str, required = False)
@lightbulb.command("current", "Get current weather")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def current_weather(ctx: lightbulb.Context) -> None:
	"""Get current weather command
	`/current [location]`
	"""
	weather 	= Weather()
	location 	= weather.location

	if ctx.options.location:
		location = ctx.options.location

	current_data = weather.get_current(location)
	icon_url = current_data["icon_url"]
	temp = round(current_data["current_temp"])
	feels_like = round(current_data["feels_like"])
	location = current_data["location"]

	embed = (
		hikari.Embed(
			title = f"Current weather in {location}",
			timestamp = datetime.now().astimezone(),
		)
		.set_footer(text=f"Your weather was brought to you by {weather.name}.")
		.set_thumbnail(icon_url)
		.add_field(
			"Temperature",
			f"{temp}°C",
			inline = True,
		)
		.add_field(
			"Feels like",
			f"{feels_like}°C",
			inline = True,
		)
	)

	await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
	bot.add_plugin(weather_plugin)
