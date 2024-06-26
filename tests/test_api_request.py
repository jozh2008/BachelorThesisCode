import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open

from pprint import pformat
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


def test_process_response_data(setup_request_syn):
    # Setup
    request = setup_request_syn
    response_data = {
        "out": {
            "format": {"mediaType": "image/tiff"},
            "href": "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff",
        }
    }

    transmission_item = {
        "format": {"mediaType": "image/tiff"},
        "href": "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff",
    }

    request.get_output_file_path = MagicMock(side_effect=lambda key: f"output_data_{key}")
    request.write_transmission_item_based_on_mode = MagicMock()

    # request.transmission_mode = {"out": "reference"}

    request.process_response_data(response_data=response_data)
    request.get_output_file_path.assert_called_once_with("out")
    request.write_transmission_item_based_on_mode.assert_called_once_with("output_data_out", transmission_item, "reference")


def test_get_output_file_path(setup_request_syn):
    # Setup
    request = setup_request_syn

    key = "out"
    result = request.get_output_file_path(key)

    expected_output = "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"

    # Assertion
    assert result == expected_output


def test_write_transmission_item_based_on_mode_raw(setup_request_raw):
    # Setup
    request = setup_request_raw
    output_file_path = (
        "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"
    )
    transmission_item = transmission_item = {
        "format": {"mediaType": "image/tiff"},
        "href": "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff",
    }
    mode = "reference"

    # Mock the write_transmission_item and write_raw_transmission_item methods
    request.write_transmission_item = MagicMock()
    request.write_raw_transmission_item = MagicMock()

    # Set response_input attribute for the instance
    # instance.response_input = "raw"

    # Test when response_input is "raw"
    request.write_transmission_item_based_on_mode(output_file_path, transmission_item, mode)

    # Assertion
    request.write_raw_transmission_item.assert_called_once_with(output_file_path, transmission_item)
    request.write_transmission_item.assert_not_called()


def test_write_transmission_item_based_on_mode_document(setup_request_syn):
    # Setup
    request = setup_request_syn
    output_file_path = (
        "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"
    )
    transmission_item = transmission_item = {
        "format": {"mediaType": "image/tiff"},
        "href": "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff",
    }
    mode = "reference"

    # Mock the write_transmission_item and write_raw_transmission_item methods
    request.write_transmission_item = MagicMock()
    request.write_raw_transmission_item = MagicMock()

    request.write_transmission_item_based_on_mode(output_file_path, transmission_item, mode)

    # Assertion
    request.write_transmission_item.assert_called_once_with(
        output_file_path=output_file_path, transmission_item=transmission_item, mode=mode
    )
    request.write_raw_transmission_item.assert_not_called()


@patch("urllib.request.urlretrieve")
def test_write_raw_transmission_item_dict(mock_urlretrieve, setup_request_raw):
    request = setup_request_raw
    output_file_path = (
        "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"
    )
    transmission_item = transmission_item = {
        "format": {"mediaType": "image/tiff"},
        "href": "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff",
    }

    request.write_raw_transmission_item(output_file_path, transmission_item)

    mock_urlretrieve.assert_called_once_with(
        "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff", output_file_path
    )


def test_write_raw_transmission_item_non_dict(setup_request_raw):
    request = setup_request_raw
    transmission_item = "some_reference"
    output_file_path = "/path/to/output/file.txt"

    # Mock write_transmission_item method
    request.write_transmission_item = MagicMock()

    request.write_raw_transmission_item(output_file_path, transmission_item)

    request.write_transmission_item.assert_called_once_with(
        output_file_path=output_file_path,
        transmission_item=transmission_item,
        mode="reference",
    )


@patch("builtins.open", new_callable=mock_open)
def test_write_transmission_item_reference_mode(mock_open, setup_request_syn):
    request = setup_request_syn
    output_file_path = (
        "/tmp/tmpyqrzc8n1/job_working_directory/000/3/outputs/dataset_f7a688b9-1bfc-4d55-a95c-82683dad7af9.dat"
    )
    transmission_item = transmission_item = {
        "format": {"mediaType": "image/tiff"},
        "href": "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff",
    }
    mode = "reference"

    request.write_transmission_item(output_file_path, transmission_item, mode)

    handle = mock_open()
    handle.write.assert_called_once_with(
        "https://ospd.geolabs.fr:8300/temp///BandMath_0_7abe2bba-360a-11ef-a61e-0242ac10ee0a.tiff\n"
    )


@patch("builtins.open", new_callable=mock_open)
def test_write_transmission_item_value_mode(mock_open_func, setup_request_syn):
    request = setup_request_syn
    transmission_item = "0"
    output_file_path = (
        "/tmp/tmphzp9pgx7/job_working_directory/000/6/outputs/dataset_73acf940-7f9d-415d-bcdb-f37cb5440ae2.dat"
    )
    mode = "value"

    request.write_transmission_item(output_file_path, transmission_item, mode)

    # Get the mock handle from the mock_open
    handle = mock_open_func()
    print(handle.write.mock_calls)

    # Construct the expected output
    expected_output = pformat(transmission_item, width=80, compact=True)

    # Assert that the write method was called with the expected output
    handle.write.assert_any_call(expected_output)

    # Assert that write was called with a newline character
    handle.write.assert_any_call("\n")

    # Assert that write was called exactly twice in total
    assert handle.write.call_count == 2
