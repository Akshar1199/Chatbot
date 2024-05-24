# Weather Chatbot

## Overview
The Weather Chatbot is an intelligent conversational agent designed to provide weather updates and basic chat interactions. It leverages Dialogflow for natural language processing and understanding, and a Flask application serves as the backend to handle the logic and data retrieval.

## Features
- **Weather Information**: Provides real-time updates on:
  - Temperature
  - Humidity
  - Weather conditions
  - Sunrise and sunset times
  - Moonrise and moonset times
  - Chances of rain and snow
- **Basic Chatting**: Engages in simple conversation to enhance user experience.
- **Integration**: Uses Dialogflow for intent recognition and response generation.

## Architecture
- **Dialogflow**: Handles the natural language understanding (NLU) and maps user queries to predefined intents.
- **Flask Application**: Serves as the backend, processing requests from Dialogflow, fetching data from weather APIs, and sending responses back to Dialogflow.


