from flask import Flask, request, jsonify
import requests
import datetime
import logging

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
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

        # Log city and date_time
        app.logger.debug('City: %s', city)
        app.logger.debug('Date-time: %s', date_time)

        if not city:
            app.logger.error("City parameter is missing")
            return jsonify({"fulfillmentText": "City parameter is missing"}), 400

        # Handle missing date-time by using current date
        if not date_time:
            current_time = datetime.datetime.now()
        else:
            try:
                # Parse date-time string
                date_part, time_part = date_time.split('T')
                time_part, timezone_part = time_part.split('+')
                hours, minutes = map(int, timezone_part.split(':'))
                date_obj = datetime.datetime.strptime(date_part, "%Y-%m-%d")
                timezone_offset = datetime.timedelta(hours=hours, minutes=minutes)
                current_time = date_obj.replace(tzinfo=datetime.timezone(timezone_offset)).astimezone(datetime.timezone.utc)
            except Exception as e:
                app.logger.error("Error parsing date-time: %s", e)
                return jsonify({"fulfillmentText": "Invalid date-time format"}), 400

        timestamp = int(current_time.timestamp())

        # Form the API request URL
        url = f"{BASE_URL}?appid={API_KEY}&q={city}"

        app.logger.debug("Request URL: %s", url)

        # Fetch weather data from OpenWeatherMap API
        response = requests.get(url)
        response_data = response.json()
        
        # Log the API response
        app.logger.debug('API response: %s', response_data)

        if response.status_code == 200 and 'weather' in response_data:
            weather_description = response_data['weather'][0]['description']
            return jsonify({"fulfillmentText": f"The weather in {city} is {weather_description}."})
        else:
            app.logger.error("Error fetching weather data: %s", response_data)
            return jsonify({"fulfillmentText": "Sorry, unable to fetch weather data."}), response.status_code

    except Exception as e:
        app.logger.error('Error processing request: %s', e)
        return jsonify({"fulfillmentText": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
