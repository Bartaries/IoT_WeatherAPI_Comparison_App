import os
import requests
import json
from flask import Flask, request, jsonify, render_template
import logging
from logs_config import setup_logging
from Machine_learning.ML_model import *

app = Flask(__name__)
DATA_FILE = 'dane.json'
setup_logging(app, level=logging.DEBUG)

API_KEY = '0b0df8b5c07548df983161807251305'
BASE_URL = (f"http://api.weatherapi.com/v1/forecast.json")

def json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            app.logger.info(
            f"Load file {DATA_FILE}"
            )
            return data
    except FileNotFoundError:
        print(f"ERROR: Plik {file_path} nie został znaleziony.")
        app.logger.error(
            f"No {file_path} file"
        )
        return None
    except json.JSONDecodeError:
        app.logger.error(
            f"Parse error in {file_path}"
        )
        return None
    except Exception as e:
        app.logger.error(
            f"Uknown error: {e}"
        )
        return None


@app.route('/api/weather', methods=['GET'])
def get_weather():
    if not API_KEY:
        app.logger.error(
            f"API Key hasn't been configured on server"
        )
        return jsonify({"error": "Klucz API nie jest skonfigurowany po stronie serwera."}), 500

    query = request.args.get('q')
    if not query:
        app.logger.error(
            f"Argument 'q' is necessary"
        )
        return jsonify({"error": "Parametr 'q' (miasto lub lat,lon) jest wymagany."}), 400

    weather_params = {
        'key': API_KEY,
        'q': query,
        'days': 1,
        'aqi': 'no',
        'alerts': 'no'
    }
    
    try:
        response = requests.get(BASE_URL, params=weather_params)
        response.raise_for_status()
        data = response.json()
        app.logger.info(
            f"API data download succesfully"
        )
        return jsonify(data)
    except requests.exceptions.HTTPError as err:
        app.logger.error(
            f"API error: {err}"
        )
        return jsonify({"error": "Błąd z API pogodowego.", "details": err.response.json()}), err.response.status_code
    except requests.exceptions.RequestException as err:
        app.logger.error(
            f"API connection problem: {err}"
        )
        return jsonify({"error": "Błąd połączenia z API pogodowym.", "details": str(err)}), 503

@app.route('/iot/weather', methods=['GET'])
def check_weather():
    iot_data = json_data(DATA_FILE)

    if iot_data is None:
        app.logger.error(
            f"{DATA_FILE} value is None"
            )
        return jsonify({"status": "error", "message": "Unable to load data"}), 500
    if not isinstance(iot_data, list) or not iot_data:
        app.logger.error(
            f"{DATA_FILE} no contain a list"
            )
        return jsonify({"status": "error", "message": "JSON file no contain a list"}), 404
    
    lastRec = iot_data[len(iot_data)-1]
    data = {
        'lastRecord': lastRec,
        'lastTimestamp': lastRec['timestamp'],
        'lastTemperature': lastRec['temperature'],
        'lastHumidity': lastRec['humidity'],
        'lastSoilIndicator': lastRec['soil'],
        'length': len(iot_data),
        'allReceived': iot_data
    }
    print(f"Timestamp: {data['lastTimestamp']}, Temp: {data['lastTemperature']}°C, Humidity: {data['lastHumidity']}%, Soil: {data['lastSoilIndicator']}, Total: {data['length']}")

    return jsonify(data)

@app.route('/prediction', methods=['GET'])
def ml_trigger():
    try:
        predict_and_plot()
        app.logger.info(
            f"ML Model triggered correctly"
        )
        return jsonify('OK'), 200
    except Exception as e:
        app.logger.error(
            f"{e}"
        )
        return jsonify('NOK'), 500
    
    

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)

    class MockApp:
        def __init__(self):
            self.logger = logging.getLogger('flask.app')

    mock_app = MockApp()
    setup_logging(mock_app, level=logging.DEBUG)

    logger = mock_app.logger
    
    print("--- Testowanie kolorowych logów ---")
    logger.debug("To jest wiadomość DEBUG (powinna być cyjanowa).")
    logger.info("To jest wiadomość INFO (powinna być zielona).")
    logger.warning("To jest wiadomość WARNING (powinna być żółta).")
    logger.error("To jest wiadomość ERROR (powinna być czerwona).")
    logger.critical("To jest wiadomość CRITICAL (powinna być magentowa).")
    print("--- Sprawdź też plik 'logs/app.log' - powinien być bez kolorów ---")
