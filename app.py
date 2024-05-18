from flask import Flask, request, jsonify
import requests
import datetime
import logging

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'
API_KEY = 'e3ae4edf3f22b50bdd318e07154d65ca'

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['POST'])
def get_weather():
    try:
        # Log the incoming request
        app.logger.debug('Received request: %s', request.get_json())

        # Get city and date_time from Dialogflow request
        request_data = request.get_json()
        city = request_data['queryResult']['parameters']['geo-city']
        date_time = request_data['queryResult']['parameters'].get('date-time', None)

        # Extract hours and minutes from the date-time string
        hours = int(date_time.split('+')[1].split(':')[0])
        minutes = int(date_time.split('+')[1].split(':')[1])

        url = BASE_URL + "appid=" + API_KEY + "&q=" + city

        if isinstance(date_time, dict) and 'startDate' in date_time and 'endDate' in date_time:
            start_date_time = date_time['startDate']

            # Extract hours and minutes from the start date-time string
            start_hours = int(start_date_time.split('+')[1].split(':')[0])
            start_minutes = int(start_date_time.split('+')[1].split(':')[1])

            # Create start timezone offset
            start_timezone_offset = datetime.timedelta(hours=start_hours, minutes=start_minutes)

            # Convert start date-time to UTC timestamp
            start_date_only = start_date_time.split('T')[0]
            start_date_obj = datetime.datetime.strptime(start_date_only, "%Y-%m-%d")
            start_date_utc = start_date_obj.replace(tzinfo=datetime.timezone(start_timezone_offset)).astimezone(datetime.timezone.utc)

            # Prepare URL for fetching weather data
            url = BASE_URL + "appid=" + API_KEY + "&q=" + city
            url += "&dt=" + str(int(start_date_utc.timestamp()))

        else:
            # Convert date_time to UTC timestamp
            date_only = date_time.split('T')[0]
            date_obj = datetime.datetime.strptime(date_only, "%Y-%m-%d")

            # Create timezone offset
            timezone_offset = datetime.timedelta(hours=hours, minutes=minutes)
            date_utc = date_obj.replace(tzinfo=datetime.timezone(timezone_offset)).astimezone(datetime.timezone.utc)

            url += "&dt=" + str(int(date_utc.timestamp()))

        # Log the URL for weather API request
        app.logger.debug('Request URL: %s', url)

        # Fetch weather data from OpenWeatherMap API
        response = requests.get(url).json()

        # Log the API response
        app.logger.debug('API response: %s', response)

        if response['cod'] == 200:
            weather_description = response['weather'][0]['description']
            return jsonify({"fulfillmentText": f"The weather in {city} is {weather_description}."})
        else:
            return jsonify({"fulfillmentText": "Sorry, unable to fetch weather data."}), 500

    except Exception as e:
        app.logger.error('Error processing request: %s', e)
        return jsonify({"fulfillmentText": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
