import pytest
import json
from app import json_data
from app import app as flask_app 


def test_json_data_happy_path(mocker):
    fake_json_content = '{"key": "value"}'
    fake_path = 'good.json'
    
    mocker.patch('builtins.open', mocker.mock_open(read_data=fake_json_content))
    
    mock_json_load = mocker.patch('app.json.load', return_value={"key": "value"})
    
    mock_logger = mocker.patch.object(flask_app, 'logger')
    
    mocker.patch('app.DATA_FILE', fake_path)

    result = json_data(fake_path)

    assert result == {"key": "value"}
    mock_json_load.assert_called_once()
    
    mock_logger.info.assert_called_once_with(f"Load file {fake_path}")

def test_json_data_file_not_found(mocker):
    fake_path = 'nonexistent.json'
    
    mocker.patch('builtins.open', side_effect=FileNotFoundError)
    
    mock_logger = mocker.patch.object(flask_app, 'logger')
    mock_print = mocker.patch('builtins.print')

    result = json_data(fake_path)

    assert result is None
    mock_print.assert_called_once_with(f"ERROR: Plik {fake_path} nie został znaleziony.")
    mock_logger.error.assert_called_once_with(f"No {fake_path} file")

def test_json_data_decode_error(mocker):
    fake_json_content = '{this is not json: "missing quotes"}'
    fake_path = 'bad.json'
    
    mocker.patch('builtins.open', mocker.mock_open(read_data=fake_json_content))
    
    mocker.patch('app.json.load', side_effect=json.JSONDecodeError("msg", "doc", 0))
    
    mock_logger = mocker.patch.object(flask_app, 'logger')

    result = json_data(fake_path)

    assert result is None
    mock_logger.error.assert_called_once_with(f"Parse error in {fake_path}")

def test_json_data_generic_exception(mocker):
    fake_path = 'permission_denied.json'
    error_message = "Permission denied"
    
    mocker.patch('builtins.open', side_effect=Exception(error_message))
    
    mock_logger = mocker.patch.object(flask_app, 'logger')

    result = json_data(fake_path)

    assert result is None
    mock_logger.error.assert_called_once_with(f"Uknown error: {error_message}")