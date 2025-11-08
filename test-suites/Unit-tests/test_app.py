import pytest
import requests
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['API_KEY'] = 'test_key_123' 
    flask_app.config['BASE_URL'] = 'http://fake-weather.com'

    with flask_app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_get_weather_no_query_param(client):
    response = client.get('/api/weather')
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Parametr 'q' (miasto lub lat,lon) jest wymagany." in json_data['error']

def test_get_weather_no_api_key(client):
    flask_app.config['API_KEY'] = None 
    
    response = client.get('/api/weather?q=London')
    assert response.status_code == 500
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Klucz API nie jest skonfigurowany" in json_data['error']
    
    flask_app.config['API_KEY'] = 'test_key_123'

def test_get_weather_happy_path(client, mocker):
    mock_response_data = {"location": {"name": "London"}, "current": {"temp_c": 15.0}}
    
    mock_get = mocker.patch('app.requests.get')
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response_data
    mock_get.return_value.raise_for_status.return_value = None 

    response = client.get('/api/weather?q=London')
    
    assert response.status_code == 200
    assert response.get_json() == mock_response_data
    
    expected_params = {
        'key': 'test_key_123',
        'q': 'London',
        'days': 1,
        'aqi': 'no',
        'alerts': 'no'
    }
    mock_get.assert_called_once_with(
        'http://fake-weather.com', 
        params=expected_params
    )

def test_get_weather_api_http_error(client, mocker):
    mock_error_response = mocker.Mock()
    mock_error_response.status_code = 500
    mock_error_response.json.return_value = {"error": {"message": "API key invalid"}}
    
    mock_get = mocker.patch('app.requests.get')
    mock_get.side_effect = requests.exceptions.HTTPError(
        "Server Error", 
        response=mock_error_response
    )

    response = client.get('/api/weather?q=London')
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Błąd z API pogodowego" in json_data['error']
    assert json_data['details'] == {"error": {"message": "API key invalid"}}

def test_get_weather_connection_error(client, mocker):
    mock_get = mocker.patch('app.requests.get')
    mock_get.side_effect = requests.exceptions.RequestException("Connection timed out")

    response = client.get('/api/weather?q=London')
    
    assert response.status_code == 503 # Service Unavailable
    json_data = response.get_json()
    assert "Błąd połączenia z API" in json_data['error']
    assert "Connection timed out" in json_data['details']