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

event_mapping = {
    "sunrise": "sunrise",
    "sunset": "sunset",
    "moonrise": "moonrise",
    "moonset": "moonset",
    "moon up": "moonrise",
    "moon down": "moonset",
    "sun up": "sunrise",
    "sun down": "sunset"
}


@app.route('/', methods=['POST'])
def get_weather():
    
    try:
    
        app.logger.debug('Received request: %s', request.get_json())

        request_data = request.get_json()
        city = request_data['queryResult']['parameters']['geo-city']
        date_time = request_data['queryResult']['parameters'].get('date-time', None)
        temperature = request_data['queryResult']['parameters'].get('get-temp', None)
        weather = request_data['queryResult']['parameters'].get('get-weather', None)
        sun_moon = request_data['queryResult']['parameters'].get('get-sun_moon', None)
        humidity = request_data['queryResult']['parameters'].get('get-humidity', None)
        rain_chance = request_data['queryResult']['parameters'].get('get-rain', None)
        snow_chance = request_data['queryResult']['parameters'].get('get-snow', None)

        # app.logger.debug('Date-time: %s', date_time)
        print("city",city)
        print("date_time",date_time)
        print("temperature",temperature)
        print("weather",weather)
        print("sun_moon",sun_moon)
        print("humidity",humidity)
        print("rain_chance",rain_chance)
        print("snow_chance",snow_chance)


        if isinstance(date_time, list) and len(date_time) == 0:
            date_obj = datetime.date.today()
            date_only = date_obj
        elif isinstance(date_time, list):
            
            if len(date_time) > 1:
                date_time = date_time[1]
            else:
                date_time = date_time[0]
        
        
        if not date_time:
            date_obj = datetime.date.today()
            date_only = date_obj
        else:
            try:
                if isinstance(date_time, list) and len(date_time) == 0:
                    date_obj = datetime.date.today()
                    date_only = date_obj
                    print("new date obj",date_obj)
                elif isinstance(date_time, list):
                    
                    if len(date_time) > 1:
                        date_time = date_time[1]
                    else:
                        date_time = date_time[0]

                date_only = date_time.split('T')[0]
                date_obj = datetime.datetime.strptime(date_only, "%Y-%m-%d").date()
                print("ak",date_only,date_obj)
            except Exception as e:
                app.logger.error("Error parsing date-time: %s", e)
                return jsonify({"fulfillmentText": "Invalid date-time format"}), 400

        app.logger.debug('Date-time: %s', date_time)

        current_date = datetime.date.today()
        date_diff = (date_obj - current_date).days
        print(date_obj, "---", date_only)
        formatted_date = date_obj.strftime("%d-%m-%Y")
        print(date_obj, "---", date_only, "---", formatted_date)

        if date_diff != 10:
            date_diff += 1
        print("currentdate", str(current_date) + " date_diff ", date_diff)


        if 10 <= date_diff <= 14:
            if date_diff in [10, 11]:
                date_diff = 10
                date_obj = current_date + datetime.timedelta(days=9)
                print("new date",date_obj)
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
        

        print("url",url)
        app.logger.debug('Request URL: %s', url)

        response = requests.get(url)
        response_data = response.json()
        app.logger.debug('API response: %s', response_data)


        if 'error' not in response_data:
            response_text = ""

            if date_diff > 14 or (10 <= date_diff <= 14 and date_diff != 9):
                forecast_day = response_data['forecast']['forecastday'][0]
                
            else:
                forecast_days = response_data['forecast']['forecastday']
                forecast_day = next((day for day in forecast_days if day['date'] == str(date_obj)), None)

            print("forecast_day",forecast_day)
            if forecast_day:

                if weather:
                    weather_description = forecast_day['day']['condition']['text']
                    response_text += f" Weather condition in {city} on {formatted_date} is {weather_description}."

                if temperature is not None:
                    temp_c = forecast_day['day']['maxtemp_c']
                    temp_f = forecast_day['day']['maxtemp_f']
                    avg_temp_c = forecast_day['day']['avgtemp_c']
                    avg_temp_f = forecast_day['day']['avgtemp_f']
                    response_text += f" The maximum temperature in {city} on {formatted_date} is {temp_c}°C ({temp_f}°F) and average temperature is {avg_temp_c}°C ({avg_temp_f}°F)."

                if sun_moon:
                    if isinstance(sun_moon, list):
                        
                        sun_moon_str = sun_moon[0]  # Assuming it's a list with a single element
                    else:
                        # sun_moon is already a string
                        sun_moon_str = sun_moon.lower()

                    event_key = event_mapping.get(sun_moon_str, None)
                    if event_key:
                        event_time = forecast_day['astro'].get(event_key, "Not available")
                        response_text += f" {sun_moon_str.capitalize()} time in {city} on {formatted_date} time is {event_time}."
                    else:
                        response_text += f" {sun_moon_str.capitalize()} is not a valid event."


                if humidity:
                    avg_humidity = forecast_day['day']['avghumidity']
                    response_text += f" The average humidity in {city} on {formatted_date} is {avg_humidity}%."

                if rain_chance:
                    if 'daily_chance_of_rain' in forecast_day['day']:
                        rain_chance = forecast_day['day']['daily_chance_of_rain']
                        response_text += f" The chance of rain in {city} on {formatted_date} is {rain_chance}%."
                    else:
                        if 'hour' in forecast_day:
                            hourly_data = forecast_day['hour']
                            total_chance_of_rain = sum(hour.get('chance_of_rain', 0) for hour in hourly_data)
                            rain_chance = total_chance_of_rain / len(hourly_data)
                            response_text += f" The chance of rain in {city} on {formatted_date} is {rain_chance}%."


                if snow_chance:
                    if 'daily_chance_of_snow' in forecast_day['day'] in forecast_day['day']:
                        snow_chance = forecast_day['day']['daily_chance_of_snow']
                        response_text += f" The chance of rain in {city} on {formatted_date} is {snow_chance}%."
                    else:
                        if 'hour' in forecast_day:
                            hourly_data = forecast_day['hour']
                            total_chance_of_snow = sum(hour.get('chance_of_snow', 0) for hour in hourly_data)
                            snow_chance = total_chance_of_snow / len(hourly_data)
                            response_text += f" The chance of rain in {city} on {formatted_date} is {snow_chance}%."

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
