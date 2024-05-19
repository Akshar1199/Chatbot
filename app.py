from flask import Flask, request, jsonify
import requests
import datetime
import logging

BASE_FORECAST_URL = 'https://api.weatherapi.com/v1/forecast.json'
BASE_FUTURE_URL = 'https://api.weatherapi.com/v1/future.json'
API_KEY = 'bfefd949b5694fe2847201736241805'

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/', methods=['POST'])
def get_weather():
    try:
    
        app.logger.debug('Received request: %s', request.get_json())

        request_data = request.get_json()
        city = request_data['queryResult']['parameters']['geo-city']
        date_time = request_data['queryResult']['parameters'].get('date-time', None)

        app.logger.debug('Date-time: %s', date_time)

        if not date_time:
            date_only = datetime.date.today()
        else:
            try:
                date_only = date_time.split('T')[0]
                date_obj = datetime.datetime.strptime(date_only, "%Y-%m-%d").date()
            except Exception as e:
                app.logger.error("Error parsing date-time: %s", e)
                return jsonify({"fulfillmentText": "Invalid date-time format"}), 400

        current_date = datetime.date.today()
        date_diff = (date_obj - current_date).days

        if date_diff > 14:
            url = f"{BASE_FUTURE_URL}?key={API_KEY}&q={city}&dt={date_only}"
        elif 0 <= date_diff <= 10:
            url = f"{BASE_FORECAST_URL}?key={API_KEY}&q={city}&days={date_diff}"
        else:
            return jsonify({"fulfillmentText": "Requested date is not valid for weather forecast."}), 400

        # Log the URL for weather API request
        app.logger.debug('Request URL: %s', url)

        # Fetch weather data from WeatherAPI
        response = requests.get(url)
        response_data = response.json()

        # Log the API response
        app.logger.debug('API response: %s', response_data)

        if 'error' not in response_data:
            if date_diff > 14:
                weather_description = response_data['forecast']['forecastday'][0]['day']['condition']['text']
            else:
                # Find the weather data for the specific requested date
                forecast_days = response_data['forecast']['forecastday']
                weather_data = next((day for day in forecast_days if day['date'] == date_only), None)
                if weather_data:
                    weather_description = weather_data['day']['condition']['text']
                else:
                    return jsonify({"fulfillmentText": "Weather data for the requested date is not available."}), 400

            return jsonify({"fulfillmentText": f"The weather in {city} on {date_only} is {weather_description}."})
        else:
            return jsonify({"fulfillmentText": "Sorry, unable to fetch weather data."}), 500

    except Exception as e:
        app.logger.error('Error processing request: %s', e)
        return jsonify({"fulfillmentText": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
