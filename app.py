from flask import Flask, request, jsonify
import requests
import datetime

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'
API_KEY = 'e3ae4edf3f22b50bdd318e07154d65ca'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hey, Ak!"})


@app.route('/', methods=['POST'])
def get_weather():
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

    response = requests.get(url).json()
    
    if response['cod'] == 200:
        weather_description = response['weather'][0]['description']
        return jsonify({"fulfillmentText": f"The weather in {city} is {weather_description}."})
    else:
        return jsonify({"fulfillmentText": "Sorry, unable to fetch weather data."})

# if __name__ == '__main__':
#     app.run(debug=True)

    
    # Check if the response is successful (status code 200)
    # if response['cod'] == 200:
    #     temperature_celsius = round(response["main"]["temp"] - 273.15, 2)

    #     # Convert sunrise and sunset times to standard time
    #     sunrise_utc = datetime.datetime.utcfromtimestamp(response["sys"]["sunrise"])
    #     sunset_utc = datetime.datetime.utcfromtimestamp(response["sys"]["sunset"])

    #     timezone_offset = datetime.timedelta(seconds=response["timezone"])

    #     sunrise_local = sunrise_utc + timezone_offset
    #     sunset_local = sunset_utc + timezone_offset

    #     # Format sunrise and sunset times
    #     sunrise_formatted = sunrise_local.strftime("%H:%M:%S %d-%m-%Y")
    #     sunset_formatted = sunset_local.strftime("%H:%M:%S %d-%m-%Y")

    #     # Create formatted weather data with units
    #     formatted_response = {
    #         "city": response["name"],
    #         "temperature": {"value": temperature_celsius, "unit": "°C"},
    #         "humidity": {"value": response["main"]["humidity"], "unit": "%"},
    #         "pressure": {"value": response["main"]["pressure"], "unit": "hPa"},
    #         "sunrise": {"value": sunrise_formatted, "unit": "UTC"},
    #         "sunset": {"value": sunset_formatted, "unit": "UTC"},
    #         "cloudiness": {"value": response["clouds"]["all"], "unit": "%"},
    #         "wind_speed": {"value": response["wind"]["speed"], "unit": "m/s"},
    #     }

#     return response
   

# if __name__ == '__main__':
#     app.run(debug=True)
