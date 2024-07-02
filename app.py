from flask import Flask, request, jsonify
import requests
import datetime
import logging
import os
from dotenv import load_dotenv

load_dotenv()

BASE_FORECAST_URL = os.getenv('BASE_FORECAST_URL')
BASE_FUTURE_URL = os.getenv('BASE_FUTURE_URL')
API_KEY = os.getenv('API_KEY')

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

event_mapping = {
    "sunrise": "sunrise",
    "sunshine": "sunrise",
    "sunset": "sunset",
    "moonrise": "moonrise",
    "moonshine": "moonrise",
    "moonset": "moonset",
    "moon up": "moonrise",
    "moon down": "moonset",
    "sun up": "sunrise",
    "sun down": "sunset"
}

def parse_date(date_str, query_text):
    try:
        print('hello')
        print('date_str:', date_str)
        print('query_text:', query_text)
        
        month_names = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

        cities = ["umarpada", "umargam", "umaria", "umarkot", "umarkhed", "marseille", "aprilia", "mayfield", "juneau", "july creek", "augusta", "octavia"]

        parts = date_str.split('-') or date_str.split('/')
        print('datetime:', parts)

        if any(city in query_text.lower() for city in cities):
            if len(parts) == 3:
                if int(parts[2]) <= 12:
                    return datetime.datetime.strptime(date_str, "%Y-%d-%m").date()
                else:
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        
        if any(month in query_text.lower() for month in month_names):
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        

        if len(parts) == 3:
            if int(parts[2]) <= 12:
                return datetime.datetime.strptime(date_str, "%Y-%d-%m").date()
            else:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
     
     
    except ValueError as e:
        app.logger.error("Error parsing date: %s", e)
        raise ValueError("Invalid date format")


@app.route('/hello', methods=['GET'])
def hello():
    print('hello')
    return "Hello, World!"

@app.route('/', methods=['POST'])
def get_weather():
    try:
        app.logger.debug('Received request: %s', request.get_json())
        request_data = request.get_json()
        print('request_data:', request_data)
        query_text = request_data['queryResult']['queryText']
        city = request_data['queryResult']['parameters']['geo-city']
        date_time = request_data['queryResult']['parameters'].get('date-time', None)
        temperature = request_data['queryResult']['parameters'].get('get-temp', None)
        weather = request_data['queryResult']['parameters'].get('get-weather', None)
        sun_moon = request_data['queryResult']['parameters'].get('get-sun_moon', None)
        humidity = request_data['queryResult']['parameters'].get('get-humidity', None)
        rain_chance = request_data['queryResult']['parameters'].get('get-rain', None)
        snow_chance = request_data['queryResult']['parameters'].get('get-snow', None)

        app.logger.debug('Date-time: %s', date_time)

        if isinstance(date_time, list) and len(date_time) == 0:
            date_obj = datetime.date.today()
        elif isinstance(date_time, list):
            date_time = date_time[0] if len(date_time) == 1 else date_time[1]

        if not date_time:
            date_obj = datetime.date.today()
        else:
            try:
                date_only = date_time.split('T')[0]
                print('date_only:', date_only)
                date_obj = parse_date(date_only, query_text)
                print('date_obj', date_obj)
            except Exception as e:
                app.logger.error("Error parsing date-time: %s", e)
                return jsonify({"fulfillmentText": "Invalid date-time format"}), 400

        app.logger.debug('Parsed date: %s', date_obj)

        current_date = datetime.date.today()
        date_diff = (date_obj - current_date).days
        formatted_date = date_obj.strftime("%d-%m-%Y")

        if datetime.time(0, 0) <= datetime.datetime.now().time() <= datetime.time(5, 0) and date_diff <= 8:
            date_diff += 2
            date_obj = current_date + datetime.timedelta(days=1)
        elif date_diff != 10:
            date_diff += 1

        if 10 <= date_diff <= 14:
            if date_diff in [10, 11]:
                date_diff = 10
                date_obj = current_date + datetime.timedelta(days=9)
                url = f"{BASE_FORECAST_URL}?key={API_KEY}&q={city}&days={date_diff}"
            else:
                date_obj = current_date + datetime.timedelta(days=15)
                url = f"{BASE_FUTURE_URL}?key={API_KEY}&q={city}&dt={date_obj}"
        elif date_diff > 14:
            url = f"{BASE_FUTURE_URL}?key={API_KEY}&q={city}&dt={date_obj}"
        elif 0 <= date_diff <= 9:
            url = f"{BASE_FORECAST_URL}?key={API_KEY}&q={city}&days={date_diff}"
        else:
            return jsonify({"fulfillmentText": "Requested date is not valid for weather forecast."}), 400

        app.logger.debug('Request URL: %s', url)

        response = requests.get(url)    
        response_data = response.json()
        app.logger.debug('API response: %s', response_data)

        if 'error' not in response_data:
            forecast_day = None

            if date_diff > 14 or (10 <= date_diff <= 14 and date_diff != 9):
                forecast_day = response_data['forecast']['forecastday'][0]
            else:
                forecast_days = response_data['forecast']['forecastday']
                forecast_day = next((day for day in forecast_days if day['date'] == str(date_obj)), None)

            if forecast_day:
                response_text = ""

                if weather:
                    weather_description = forecast_day['day']['condition']['text']
                    response_text += f"Weather condition is {weather_description},"

                if temperature:
                    temp_c = forecast_day['day']['maxtemp_c']
                    temp_f = forecast_day['day']['maxtemp_f']
                    avg_temp_c = forecast_day['day']['avgtemp_c']
                    avg_temp_f = forecast_day['day']['avgtemp_f']
                    response_text += f" The maximum temperature is {temp_c}°C ({temp_f}°F) and average temperature is {avg_temp_c}°C ({avg_temp_f}°F),"

                if sun_moon:
                    if isinstance(sun_moon, list):
                        for event in sun_moon:
                            event_key = event_mapping.get(event.lower(), None)
                            if event_key:
                                event_time = forecast_day['astro'].get(event_key, "Not available")
                                response_text += f" {event.capitalize()} time is {event_time},"  
                            else:
                                response_text += f" {event.capitalize()} is not a valid event,"             
                    else:   
                        sun_moon_str = sun_moon.lower()
                        event_key = event_mapping.get(sun_moon_str, None)
                        if event_key:
                            event_time = forecast_day['astro'].get(event_key, "Not available")
                            response_text += f" {sun_moon_str.capitalize()} time is {event_time},"
                        else:
                            response_text += f" {sun_moon_str.capitalize()} is not a valid event."

                if humidity:
                    avg_humidity = forecast_day['day']['avghumidity']
                    response_text += f" The average humidity is {avg_humidity}%,"

                if rain_chance:
                    if 'daily_chance_of_rain' in forecast_day['day']:
                        rain_chance = forecast_day['day']['daily_chance_of_rain']
                        response_text += f" The chance of rain is {rain_chance}%,"
                    else:
                        hourly_data = forecast_day['hour']
                        total_chance_of_rain = sum(hour.get('chance_of_rain', 0) for hour in hourly_data)
                        rain_chance = round(total_chance_of_rain / len(hourly_data), 2)
                        response_text += f" The chance of rain is {rain_chance}%,"


                if snow_chance:
                    if 'daily_chance_of_snow' in forecast_day['day']:
                        snow_chance = forecast_day['day']['daily_chance_of_snow']
                        response_text += f" The chance of snow is {snow_chance}%,"
                    else:
                        hourly_data = forecast_day['hour']
                        total_chance_of_snow = sum(hour.get('chance_of_snow', 0) for hour in hourly_data)
                        snow_chance = round(total_chance_of_snow / len(hourly_data), 2)
                        response_text += f" The chance of snow is {snow_chance}%,"

                response_text += f" in {city} on {formatted_date}"

                return jsonify({"fulfillmentText": response_text})
            
            else:
                return jsonify({"fulfillmentText": "Weather data for the requested date is not available."}), 400
            
        else:
            return jsonify({"fulfillmentText": "Sorry, unable to fetch weather data."}), 500

    except Exception as e:
        app.logger.error('Error processing request: %s', e)
        return jsonify({"fulfillmentText": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
