from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['POST'])
def get_weather():
    try:
        app.logger.debug('Received request: %s', request.get_json())
        return jsonify({"fulfillmentText": "Hello from Flask!"})
    except Exception as e:
        app.logger.error('Error processing request: %s', e)
        return jsonify({"fulfillmentText": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
