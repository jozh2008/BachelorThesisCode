import pytest

from unittest.mock import patch, Mock

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
        "output_data_out": (
            "/tmp/tmpv7_din2m/job_working_directory/" "000/7/outputs/dataset_e90b18c4-7615-464f-9399-6d0bbca093de.dat"
        ),
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
        "output_data_out": (
            "/tmp/tmpv7_din2m/job_working_directory/" "000/21/outputs/dataset_ac1be78d-bfbd-44ce-a32f-8c6777713b41.dat"
        ),
        "ram": "256",
    }

    mock_extract_data_files.return_value = {
        "il": "/tmp/tmpv7_din2m/files/a/2/d/dataset_a2de679f-7d52-4c07-9fca-8f61ac768ff9.dat",
        "output_data_out": (
            "/tmp/tmpv7_din2m/job_working_directory/" "000/21/outputs/dataset_ac1be78d-bfbd-44ce-a32f-8c6777713b41.dat"
        ),
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


@patch.object(ApiJson, "open_and_read_file")
def test_process_and_generate_input_files_without_array(mock_open_and_read_file, setup_JSON):
    processor = setup_JSON

    mock_open_and_read_file.side_effect = lambda file_path: f"Contents of {file_path}"

    # Mock data for input_files and input_schema
    input_files = {"file1": "/tmp/files/data1.txt", "output_data_file": "/tmp/outputs/data2.txt"}

    input_schema = {"isArrayfile1": "False"}

    # Mocking other methods called within process_and_generate_input_files if needed
    processor.generate_input_file_json = Mock(
        side_effect=lambda input_name, input_list: {"input_name": input_name, "input_list": input_list}
    )
    processor.generate_input_file_list_json = Mock(
        side_effect=lambda input_name, input_list: {"input_name_list": input_name, "input_list": input_list}
    )

    # Call the method under test
    result = processor.process_and_generate_input_files(input_files, input_schema)

    # Assertions
    expected_json = {"input_list": "Contents of /tmp/files/data1.txt", "input_name": "file1"}

    assert expected_json in result

    # Check exclusion list and file directory if needed
    assert "isArrayfile1" in processor.exclusion_list
    assert "output_data_file" in processor.exclusion_list
    assert processor.file_directory["output_data_file"] == "/tmp/outputs/data2.txt"


def test_generate_input_file_json(setup_JSON):
    processor = setup_JSON
    input_name = "file1"
    input_list = ["/tmp/files/data1.txt"]

    expected_output = {
        "file1": {"href": "/tmp/files/data1.txt"},
    }

    result = processor.generate_input_file_json(input_name, input_list)

    assert result == expected_output


def test_generate_input_file_list_json(setup_JSON):
    processor = setup_JSON
    input_name = "file_list"
    input_list = ["/tmp/files/data1.txt", "/tmp/files/data2.txt", "/tmp/files/data3.txt"]
    expected_output = {
        "file_list": [{"href": "/tmp/files/data1.txt"}, {"href": "/tmp/files/data2.txt"}, {"href": "/tmp/files/data3.txt"}]
    }
    assert processor.generate_input_file_list_json(input_name, input_list) == expected_output


# Test case 1: Basic functionality with default prefix
def test_extract_suffix_after_prefix_default_prefix(setup_JSON):
    processor = setup_JSON
    key = "output_data_suffix"
    expected_suffix = "suffix"
    assert processor.extract_suffix_after_prefix(key) == expected_suffix


# Test case 2: Custom prefix with valid suffix
def test_extract_suffix_after_prefix_custom_prefix(setup_JSON):
    processor = setup_JSON
    key = "custom_prefix_suffix"
    prefix = "custom_prefix"
    expected_suffix = "suffix"
    assert processor.extract_suffix_after_prefix(key, prefix) == expected_suffix


# Test case 3: Custom prefix not found in key
def test_extract_suffix_after_prefix_prefix_not_found(setup_JSON):
    processor = setup_JSON
    key = "data_suffix"
    prefix = "output_data"
    expected_suffix = ""
    assert processor.extract_suffix_after_prefix(key, prefix) == expected_suffix


# Test case 4: Empty key
def test_extract_suffix_after_prefix_empty_key(setup_JSON):
    processor = setup_JSON
    key = ""
    prefix = "output_data"
    expected_suffix = ""
    assert processor.extract_suffix_after_prefix(key, prefix) == expected_suffix


# Test case 5: Key with only prefix
def test_extract_suffix_after_prefix_only_prefix(setup_JSON):
    processor = setup_JSON
    key = "output_data"
    prefix = "output_data"
    expected_suffix = ""
    assert processor.extract_suffix_after_prefix(key, prefix) == expected_suffix


# Test case 6: Key with prefix followed by special characters
def test_extract_suffix_after_prefix_special_characters(setup_JSON):
    processor = setup_JSON
    key = "output_data-suffix"
    prefix = "output_data"
    expected_suffix = "suffix"
    assert processor.extract_suffix_after_prefix(key, prefix) == expected_suffix


# Test case 7: Key with prefix as part of another word
def test_extract_suffix_after_prefix_partial_match(setup_JSON):
    processor = setup_JSON
    key = "output_data_suffix"
    prefix = "output_data"
    expected_suffix = "suffix"
    assert processor.extract_suffix_after_prefix(key, prefix) == expected_suffix


# Test case 8: Key with prefix at the end
def test_extract_suffix_after_prefix_prefix_at_end(setup_JSON):
    processor = setup_JSON
    key = "suffix_output_data"
    prefix = "output_data"
    expected_suffix = ""
    assert processor.extract_suffix_after_prefix(key, prefix) == expected_suffix


# Test case 1: Exclude specific data inputs
def test_extract_non_data_inputs_exclude_data_inputs(setup_JSON):
    processor = setup_JSON
    data_inputs = {
        "il": "/tmp/tmpv7_din2m/files/a/2/d/dataset_a2de679f-7d52-4c07-9fca-8f61ac768ff9.dat",
        "output_data_out": (
            "/tmp/tmpv7_din2m/job_working_directory/" "000/21/outputs/dataset_ac1be78d-bfbd-44ce-a32f-8c6777713b41.dat"
        ),
    }
    all_input_values = {
        "exp": "im1b1+im1b2",
        "il": "/tmp/tmpv7_din2m/files/a/2/d/dataset_a2de679f-7d52-4c07-9fca-8f61ac768ff9.dat",
        "isArrayil": "True",
        "out": "float",
        "output_data_out": (
            "/tmp/tmpv7_din2m/job_working_directory/" "000/21/outputs/dataset_ac1be78d-bfbd-44ce-a32f-8c6777713b41.dat"
        ),
        "ram": "256",
    }
    processor.exclusion_list = ["isArrayil"]
    expected_output = {"exp": "im1b1+im1b2", "out": "float", "ram": "256"}
    assert processor.extract_non_data_inputs(data_inputs, all_input_values) == expected_output


# Test case 2: No data inputs provided
def test_extract_non_data_inputs_no_data_inputs(setup_JSON):
    processor = setup_JSON
    data_inputs = {}
    all_input_values = {"input1": "value1", "input2": "value2"}
    expected_output = {"input1": "value1", "input2": "value2"}
    assert processor.extract_non_data_inputs(data_inputs, all_input_values) == expected_output


def test_extract_data_files(setup_JSON):
    extractor = setup_JSON
    input_dict = {"file1": "data1.dat", "file2": "data2.txt", "exp": "im1b1+im1b2", "out": "float", "ram": "256"}
    expected_output = {"file1": "data1.dat", "file2": "data2.txt"}
    assert extractor.extract_data_files(input_dict) == expected_output


def test_extract_input_values(setup_JSON):
    extractor = setup_JSON
    input_dict = {
        "response_time": "100ms",
        "outputType_file": "data.txt",
        "transmissionMode_secure": "enabled",
        "name_user": "Alice",
        "prefer_mode": "fast",
        "input_data": "value1",
    }
    expected_output = {"input_data": "value1"}
    assert extractor.extract_input_values(input_dict) == expected_output


def test_extract_values_by_keyword(setup_JSON):
    extractor = setup_JSON
    input_dict = {
        "response_time": "100ms",
        "outputType_file": "data.txt",
        "transmissionMode_secure": "enabled",
        "input_data": "value1",
        "outputType_speed": "fast",
    }
    expected_output = {"file": "data.txt", "speed": "fast"}
    assert extractor.extract_values_by_keyword(input_dict, "outputType") == expected_output


def test_extract_output_values(setup_JSON):
    extractor = setup_JSON
    input_dict = {
        "response_time": "100ms",
        "outputType_file": "data.txt",
        "outputType_speed": "fast",
        "input_data": "value1",
    }
    expected_output = {"file": "data.txt", "speed": "fast"}
    assert extractor.extract_output_values(input_dict) == expected_output


def test_extract_transmission_mode_values(setup_JSON):
    extractor = setup_JSON
    input_dict = {
        "response_time": "100ms",
        "transmissionMode_secure": "enabled",
        "transmissionMode_mode": "auto",
        "input_data": "value1",
    }
    expected_output = {"secure": "enabled", "mode": "auto"}
    assert extractor.extract_transmission_mode_values(input_dict) == expected_output


def test_extract_response_value(setup_JSON):
    extractor = setup_JSON
    input_dict = {"outputType_file": "data.txt", "response_code": "200", "input_data": "value1"}
    expected_output = "200"
    assert extractor.extract_response_value(input_dict) == expected_output


def test_generate_output_list(setup_JSON):
    extractor = setup_JSON
    input_attributes = {
        "outputType_file_image": "image/jpeg",
        "outputType_file_text": "text/plain",
        "transmissionMode_file_image": "online",
        "transmissionMode_file_text": "offline",
        "outputType_file_data": "application/json",
        "transmissionMode_file_data": "secure",
    }
    expected_output = [
        {"file.image": {"format": {"mediaType": "image/jpeg"}, "transmissionMode": "reference"}},
        {"file.text": {"format": {"mediaType": "text/plain"}, "transmissionMode": "offline"}},
        {"file.data": {"format": {"mediaType": "application/json"}, "transmissionMode": "secure"}},
    ]
    assert (
        extractor.generate_output_list(input_attributes) == expected_output
    ), f"Expected:\n{input_attributes}\n\nActual:\n{expected_output}"


def test_create_input_json(setup_JSON):
    extractor = setup_JSON
    non_data_inputs = {"param1": "value1", "param2": "value2"}
    input_files = [{"file1": "path/to/file1"}, {"file2": "path/to/file2"}]
    expected_output = {"param1": "value1", "param2": "value2", "file1": "path/to/file1", "file2": "path/to/file2"}
    assert extractor.create_input_json(non_data_inputs, input_files) == expected_output


def test_combine_dicts(setup_JSON):
    extractor = setup_JSON
    dict_list = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]
    expected_output = {"a": 1, "b": 3, "c": 4}
    assert extractor.combine_dicts(dict_list) == expected_output


def test_merge_dicts(setup_JSON):
    extractor = setup_JSON
    base_dict = {"a": 1, "b": 2}
    overlay_dict = {"b": 3, "c": 4}
    expected_output = {"a": 1, "b": 3, "c": 4}
    assert extractor.merge_dicts(base_dict, overlay_dict) == expected_output


def test_get_process_execution(setup_JSON):
    extractor = setup_JSON
    input_attributes = {"name": "exampleProcess"}
    expected_output = "processes/exampleProcess/execution"
    assert extractor.get_process_execution(input_attributes) == expected_output
