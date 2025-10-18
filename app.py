import os
import requests
from flask import Flask, request, jsonify, render_template


app = Flask(__name__)

API_KEY = '0b0df8b5c07548df983161807251305' # <------ Nie mam premki więc dużo tych requestów chyba nie można XDDDD albo chyba tylko na żywo
BASE_URL = (f"http://api.weatherapi.com/v1/forecast.json")


@app.route('/api/weather', methods=['GET'])
def get_weather():
    if not API_KEY:
        return jsonify({"error": "Klucz API nie jest skonfigurowany po stronie serwera."}), 500

    query = request.args.get('q')
    if not query:
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
        return jsonify(data)
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Błąd z API pogodowego.", "details": err.response.json()}), err.response.status_code
    except requests.exceptions.RequestException as err:
        return jsonify({"error": "Błąd połączenia z API pogodowym.", "details": str(err)}), 503

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
