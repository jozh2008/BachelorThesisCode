import pytest

from unittest.mock import Mock, patch

import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Tools", "Code")))

from Tools.Code.openapi import ApiJson


@pytest.fixture
def setup_JSON():
    json = ApiJson()

    return json


def test_convert_even_args(setup_JSON):
    converter = setup_JSON
    assert converter.convert(["key1", "value1", "key2", "value2"]) == {"key1": "value1", "key2": "value2"}
    assert converter.convert(["a", 1, "b", 2]) == {"a": 1, "b": 2}


def test_convert_empty_args(setup_JSON):
    converter = setup_JSON
    assert converter.convert([]) == {}


def test_convert_odd_args(setup_JSON):
    converter = setup_JSON
    with pytest.raises(ValueError):
        converter.convert(["key1", "value1", "key2"])


@patch.object(ApiJson, "extract_input_values")
@patch.object(ApiJson, "extract_data_files")
@patch.object(ApiJson, "process_and_generate_input_files")
@patch.object(ApiJson, "extract_non_data_inputs")
@patch.object(ApiJson, "modify_attributes")
@patch.object(ApiJson, "create_input_json")
def test_process_input_values(
    mock_create_input_json,
    mock_modify_attributes,
    mock_extract_non_data_inputs,
    mock_process_and_generate_input_files,
    mock_extract_data_files,
    mock_extract_input_values,
    setup_JSON,
):
    tool = setup_JSON

    attributes = {
        "exp": "im1b1+im1b2",
        "il": "/tmp/tmpv7_din2m/files/d/d/9/dataset_dd971958-b8c7-4c64-9dd7-ac8fb8a707d0.dat",
        "isArrayil": "True",
        "name": "OTB.BandMath",
        "out": "float",
        "outputType_out": "image/jpeg",
        "output_data_out": "/tmp/tmpv7_din2m/job_working_directory/000/7/outputs/dataset_e90b18c4-7615-464f-9399-6d0bbca093de.dat",
        "prefer": "return=representation",
        "ram": "256",
        "response": "raw",
        "transmissionMode_out": "reference",
    }
    mock_extract_input_values.return_value = {
        "exp": "im1b1+im1b2",
        "il": "/tmp/tmpv7_din2m/files/a/2/d/dataset_a2de679f-7d52-4c07-9fca-8f61ac768ff9.dat",
        "isArrayil": "True",
        "out": "float",
        "output_data_out": "/tmp/tmpv7_din2m/job_working_directory/000/21/outputs/dataset_ac1be78d-bfbd-44ce-a32f-8c6777713b41.dat",
        "ram": "256",
    }
    mock_extract_data_files.return_value = {
        "il": "/tmp/tmpv7_din2m/files/a/2/d/dataset_a2de679f-7d52-4c07-9fca-8f61ac768ff9.dat",
        "output_data_out": "/tmp/tmpv7_din2m/job_working_directory/000/21/outputs/dataset_ac1be78d-bfbd-44ce-a32f-8c6777713b41.dat",
    }
    mock_process_and_generate_input_files.return_value = [{"il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}]}]
    mock_extract_non_data_inputs.return_value = {"exp": "im1b1+im1b2", "out": "float", "ram": "256"}
    mock_modify_attributes.return_value = {"exp": "im1b1+im1b2", "out": "float", "ram": "256"}
    mock_create_input_json.return_value = {
        "exp": "im1b1+im1b2",
        "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
        "out": "float",
        "ram": "256",
    }
    result = tool.process_input_values(attributes)

    mock_extract_input_values.assert_called_once_with(attributes)
    mock_extract_data_files.assert_called_once_with(mock_extract_input_values.return_value)
    mock_process_and_generate_input_files.assert_called_once_with(
        mock_extract_data_files.return_value,
        mock_extract_input_values.return_value,
    )
    mock_extract_non_data_inputs.assert_called_once_with(
        data_inputs=mock_extract_data_files.return_value,
        all_input_values=mock_extract_input_values.return_value,
    )
    mock_modify_attributes.assert_called_once_with(mock_extract_non_data_inputs.return_value)
    mock_create_input_json.assert_called_once_with(
        non_data_inputs=mock_modify_attributes.return_value,
        input_files=mock_process_and_generate_input_files.return_value,
    )

    assert result == mock_create_input_json.return_value
