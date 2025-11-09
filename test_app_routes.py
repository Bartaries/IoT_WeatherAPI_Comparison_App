import pytest
import requests
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    
    with flask_app.test_client() as client:
        yield client

def test_get_weather_no_api_key_configured(client, mocker):
    mocker.patch('app.API_KEY', None)
    
    mock_logger = mocker.patch.object(flask_app, 'logger')

    response = client.get('/api/weather?q=London')

    assert response.status_code == 500
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Klucz API nie jest skonfigurowany" in json_data['error']
    mock_logger.error.assert_called_once_with("API Key hasn't been configured on server")

def test_get_weather_no_query_param(client, mocker):
    mocker.patch('app.API_KEY', 'test_key_123')
    
    mock_logger = mocker.patch.object(flask_app, 'logger')

    response = client.get('/api/weather')

    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Parametr 'q' (miasto lub lat,lon) jest wymagany." in json_data['error']
    mock_logger.error.assert_called_once_with("Argument 'q' is necessary")

def test_get_weather_happy_path_success(client, mocker):
    mocker.patch('app.API_KEY', 'test_key_123')
    mocker.patch('app.BASE_URL', 'http://fake-weather-api.com')

    fake_api_response_data = {"location": {"name": "London"}, "current": {"temp_c": 15.0}}

    mock_get = mocker.patch('app.requests.get')
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = fake_api_response_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    mock_logger = mocker.patch.object(flask_app, 'logger')

    response = client.get('/api/weather?q=London')

    assert response.status_code == 200
    assert response.get_json() == fake_api_response_data
    
    expected_params = {
        'key': 'test_key_123',
        'q': 'London',
        'days': 1,
        'aqi': 'no',
        'alerts': 'no'
    }
    mock_get.assert_called_once_with(
        'http://fake-weather-api.com', 
        params=expected_params
    )
    
    mock_logger.info.assert_called_once_with("API data download succesfully")

def test_get_weather_api_http_error(client, mocker):

    mocker.patch('app.API_KEY', 'test_key_123')
    mocker.patch('app.BASE_URL', 'http://fake-weather-api.com')

    fake_api_error_details = {"error": {"message": "API key invalid or something"}}

    mock_error_response = mocker.Mock()
    mock_error_response.status_code = 500
    mock_error_response.json.return_value = fake_api_error_details
    
    mock_get = mocker.patch('app.requests.get')
    mock_get.side_effect = requests.exceptions.HTTPError(
        "Internal Server Error",
        response=mock_error_response
    )

    mock_logger = mocker.patch.object(flask_app, 'logger')
    
    response = client.get('/api/weather?q=London')

    assert response.status_code == 500
    json_data = response.get_json()
    assert "Błąd z API pogodowego" in json_data['error']
    assert json_data['details'] == fake_api_error_details
    assert mock_logger.error.call_count == 1

def test_get_weather_connection_error(client, mocker):
    mocker.patch('app.API_KEY', 'test_key_123')
    mocker.patch('app.BASE_URL', 'http://fake-weather-api.com')

    mock_get = mocker.patch('app.requests.get')
    error_message = "Connection timed out"
    mock_get.side_effect = requests.exceptions.RequestException(error_message)

    mock_logger = mocker.patch.object(flask_app, 'logger')

    response = client.get('/api/weather?q=London')

    assert response.status_code == 503
    json_data = response.get_json()
    assert "Błąd połączenia z API" in json_data['error']
    assert json_data['details'] == error_message
    assert mock_logger.error.call_count == 1