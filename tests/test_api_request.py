import pytest
from unittest.mock import Mock, patch, MagicMock


import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Tools", "Code")))

from Tools.Code.api_request import APIRequest


@pytest.fixture
def setup_request_syn():
    execute = "processes/OTB.BandMath/execution"
    payload = {
        "inputs": {
            "exp": "im1b1+im1b2",
            "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
            "out": "float",
            "ram": "256",
        },
        "outputs": {"out": {"format": {"mediaType": "image/tiff"}, "transmissionMode": "reference"}},
        "response": "document",
    }
    response_input = "document"
    output_format_dictionary = {"out": "image/tiff"}
    file_directory = {
        "output_data_out": "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"
    }
    transmission_mode = {"out": "reference"}
    prefer = "return=representation"

    request = APIRequest(
        execute=execute,
        payload=payload,
        response_input=response_input,
        output_format_dictionary=output_format_dictionary,
        file_directory=file_directory,
        transmission_mode=transmission_mode,
        prefer=prefer,
    )

    return request


@pytest.fixture
def setup_request_asyn():
    execute = "processes/OTB.BandMath/execution"
    payload = {
        "inputs": {
            "exp": "im1b1+im1b2",
            "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
            "out": "float",
            "ram": "256",
        },
        "outputs": {"out": {"format": {"mediaType": "image/tiff"}, "transmissionMode": "reference"}},
        "response": "document",
    }
    response_input = "document"
    output_format_dictionary = {"out": "image/tiff"}
    file_directory = {
        "output_data_out": "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"
    }
    transmission_mode = {"out": "reference"}
    prefer = "respond-async;return=representation"

    request = APIRequest(
        execute=execute,
        payload=payload,
        response_input=response_input,
        output_format_dictionary=output_format_dictionary,
        file_directory=file_directory,
        transmission_mode=transmission_mode,
        prefer=prefer,
    )

    return request


@pytest.fixture
def setup_request_raw():
    execute = "processes/OTB.BandMath/execution"
    payload = {
        "inputs": {
            "exp": "im1b1+im1b2",
            "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
            "out": "float",
            "ram": "256",
        },
        "outputs": {"out": {"format": {"mediaType": "image/png"}, "transmissionMode": "reference"}},
        "response": "document",
    }
    response_input = "raw"
    output_format_dictionary = {"out": "image/png"}
    file_directory = {
        "output_data_out": "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"
    }
    transmission_mode = {"out": "reference"}
    prefer = "respond-async;return=representation"

    request = APIRequest(
        execute=execute,
        payload=payload,
        response_input=response_input,
        output_format_dictionary=output_format_dictionary,
        file_directory=file_directory,
        transmission_mode=transmission_mode,
        prefer=prefer,
    )

    return request


def test_handle_response_error(capsys, setup_request_syn):
    example_instance = setup_request_syn
    response_mock = Mock()

    # Test case for specific error message
    response_mock.status_code = 404
    example_instance.handle_response_error(response_mock)
    captured = capsys.readouterr()
    assert captured.err == "404 Not Found\n"

    response_mock.status_code = 500
    example_instance.handle_response_error(response_mock)
    captured = capsys.readouterr()
    assert captured.err == "500 Internal Server Error\n"

    response_mock.status_code = 405
    example_instance.handle_response_error(response_mock)
    captured = capsys.readouterr()
    assert captured.err == "405 Method Not Allowed\n"

    response_mock.status_code = 400
    example_instance.handle_response_error(response_mock)
    captured = capsys.readouterr()
    assert captured.err == "400 Bad Request\n"

    # Test case for generic error message
    response_mock.status_code = 401
    example_instance.handle_response_error(response_mock)
    captured = capsys.readouterr()
    assert captured.err == "Error with HTTP response status code: 401\n"


def test_get_url(setup_request_syn):
    request = setup_request_syn

    request.job_id = "12345"  # Set the job_id for testing

    # Test for "execute" keyword
    assert request.get_url("execute") == "https://ospd.geolabs.fr:8300/ogc-api/processes/OTB.BandMath/execution"

    # Test for "jobs" keyword
    assert request.get_url("jobs") == "https://ospd.geolabs.fr:8300/ogc-api/jobs/12345"

    # Test for "results" keyword
    assert request.get_url("results") == "https://ospd.geolabs.fr:8300/ogc-api/jobs/12345/results"

    # Test for invalid keyword
    with pytest.raises(KeyError):
        request.get_url("invalid")


# Mocks for requests.get and time.sleep
@patch("requests.get")
@patch("time.sleep", return_value=None)
def test_check_job_id(mock_sleep, mock_get, setup_request_asyn):
    request = setup_request_asyn

    # Mock the initial response from the POST request
    initial_response = MagicMock()
    initial_response.status_code = 201
    initial_response.json.return_value = {"status": "running", "jobID": "12345"}

    # Mock the subsequent responses from the GET request
    running_response = MagicMock()
    running_response.json.return_value = {"status": "running"}

    successful_response = MagicMock()
    successful_response.json.return_value = {"status": "successful"}

    mock_get.side_effect = [running_response, successful_response, successful_response]

    final_response = request.check_job_id(initial_response)

    # Check that the job_id is set correctly
    assert request.job_id == "12345"

    # Check that the final status is "successful"
    assert final_response.json()["status"] == "successful"

    # Ensure the sleep was called
    assert mock_sleep.call_count == 2

    # Check the calls to requests.get
    assert mock_get.call_count == 3
    mock_get.assert_any_call(url="https://ospd.geolabs.fr:8300/ogc-api/jobs/12345", headers={"accept": "application/json"})
    mock_get.assert_any_call(
        url="https://ospd.geolabs.fr:8300/ogc-api/jobs/12345/results", headers={"accept": "application/json"}
    )
