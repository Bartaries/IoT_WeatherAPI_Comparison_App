import os
import requests
from flask import Flask, request, jsonify, render_template
import logging
from logs_config import setup_logging


app = Flask(__name__)
setup_logging(app, level=logging.DEBUG)

API_KEY = '0b0df8b5c07548df983161807251305' # <------ Nie mam premki więc dużo tych requestów chyba nie można XDDDD albo chyba tylko na żywo
BASE_URL = (f"http://api.weatherapi.com/v1/forecast.json")


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

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
