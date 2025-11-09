import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_check_weather_happy_path(client, mocker):
    fake_record = {
        "timestamp": "2025-11-09T12:00:00",
        "temperature": 22.5,
        "humidity": 55.0,
        "soil": 3
    }
    fake_iot_data = [
        {"timestamp": "...", "temperature": 20, "humidity": 50, "soil": 2},
        fake_record
    ]
    
    mock_json_data = mocker.patch('app.json_data', return_value=fake_iot_data)
    mocker.patch('app.DATA_FILE', 'fake.json')
    mock_print = mocker.patch('builtins.print')
    
    response = client.get('/iot/weather') 
    
    assert response.status_code == 200
    json_response = response.get_json()
    
    assert json_response['lastRecord'] == fake_record
    assert json_response['lastTemperature'] == 22.5
    assert json_response['length'] == 2
    assert json_response['allReceived'] == fake_iot_data
    
    mock_json_data.assert_called_once_with('fake.json')
    
    expected_print = "Timestamp: 2025-11-09T12:00:00, Temp: 22.5°C, Humidity: 55.0%, Soil: 3, Total: 2"
    mock_print.assert_called_once_with(expected_print)

def test_check_weather_json_data_returns_none(client, mocker):
    mock_json_data = mocker.patch('app.json_data', return_value=None)
    mocker.patch('app.DATA_FILE', 'fake.json')
    mock_logger = mocker.patch.object(flask_app, 'logger')

    response = client.get('/iot/weather')
    
    assert response.status_code == 500
    json_response = response.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Unable to load data'
    
    mock_logger.error.assert_called_once_with("fake.json value is None")

def test_check_weather_json_data_is_empty_list(client, mocker):
    mock_json_data = mocker.patch('app.json_data', return_value=[])
    mocker.patch('app.DATA_FILE', 'empty.json')
    mock_logger = mocker.patch.object(flask_app, 'logger')

    response = client.get('/iot/weather')
    
    assert response.status_code == 404
    json_response = response.get_json()
    assert json_response['message'] == 'JSON file no contain a list'
    
    mock_logger.error.assert_called_once_with("empty.json no contain a list")

def test_check_weather_json_data_is_not_list(client, mocker):
    mock_json_data = mocker.patch('app.json_data', return_value={"to": "nie jest lista"})
    mocker.patch('app.DATA_FILE', 'dict.json')
    mock_logger = mocker.patch.object(flask_app, 'logger')

    response = client.get('/iot/weather')
    
    assert response.status_code == 404
    
    mock_logger.error.assert_called_once_with("dict.json no contain a list")