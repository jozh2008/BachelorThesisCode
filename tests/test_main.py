import pytest

# import requests
import requests_mock

# import json
# import os
from unittest.mock import patch, mock_open
from main import Initialize


@pytest.fixture
def mock_collections_data():
    return {
        "id": "OTB.BandMath",
        "version": "1.0.0",
        "title": "Outputs a monoband image which is the result of a mathematical operation on several multi-band images.",
        "description": (
            "This application performs a mathematical operation on several multi-band images "
            "and outputs the result into a monoband image. The given expression is computed at "
            "each pixel position. Evaluation of the mathematical formula is done by the muParser "
            "library. The formula can be written using:\n"
            "- numerical values (e.g., 2.3, -5, 3.1e4, ...)\n"
            "- variables containing pixel values (e.g., `im2b3` is the pixel value in 2nd image, 3rd band)\n"
            "- binary operators:\n"
            "  - `+` addition\n"
            "  - `-` subtraction\n"
            "  - `*` multiplication\n"
            "  - `/` division\n"
            "  - `^` raise x to the power of y"
        ),
        "inputs": {
            "exp": {
                "description": "The muParser mathematical expression to apply on " "input images.",
                "schema": {"type": "string"},
                "title": "The muParser mathematical expression to apply on input " "images.",
            },
            "il": {
                "description": "Image list of operands to the mathematical expression.",
                "extended-schema": {
                    "items": {
                        "oneOf": [
                            {
                                "allOf": [
                                    {"$ref": "http://zoo-project.org/dl/link.json"},
                                    {
                                        "properties": {"type": {"enum": ["image/tiff", "image/jpeg", "image/png"]}},
                                        "type": "object",
                                    },
                                ]
                            },
                            {
                                "properties": {
                                    "value": {
                                        "oneOf": [
                                            {"contentEncoding": "base64", "contentMediaType": "image/tiff", "type": "string"},
                                            {"contentEncoding": "base64", "contentMediaType": "image/jpeg", "type": "string"},
                                            {"contentEncoding": "base64", "contentMediaType": "image/png", "type": "string"},
                                        ]
                                    }
                                },
                                "required": ["value"],
                                "type": "object",
                            },
                        ]
                    },
                    "maxItems": 1024,
                    "minItems": 1,
                    "type": "array",
                },
                "maxOccurs": 1024,
                "schema": {
                    "oneOf": [
                        {"contentEncoding": "base64", "contentMediaType": "image/tiff", "type": "string"},
                        {"contentEncoding": "base64", "contentMediaType": "image/jpeg", "type": "string"},
                        {"contentEncoding": "base64", "contentMediaType": "image/png", "type": "string"},
                    ]
                },
                "title": "Image list of operands to the mathematical expression.",
            },
        },
        "outputs": {
            "out": {
                "description": "Output image which is the result of the mathematical "
                "expressions on input image list operands.",
                "extended-schema": {
                    "oneOf": [
                        {
                            "allOf": [
                                {"$ref": "http://zoo-project.org/dl/link.json"},
                                {"properties": {"type": {"enum": ["image/tiff", "image/jpeg", "image/png"]}}, "type": "object"},
                            ]
                        },
                        {
                            "properties": {
                                "value": {
                                    "oneOf": [
                                        {"contentEncoding": "base64", "contentMediaType": "image/tiff", "type": "string"},
                                        {"contentEncoding": "base64", "contentMediaType": "image/jpeg", "type": "string"},
                                        {"contentEncoding": "base64", "contentMediaType": "image/png", "type": "string"},
                                    ]
                                }
                            },
                            "required": ["value"],
                            "type": "object",
                        },
                    ]
                },
                "schema": {
                    "oneOf": [
                        {"contentEncoding": "base64", "contentMediaType": "image/tiff", "type": "string"},
                        {"contentEncoding": "base64", "contentMediaType": "image/jpeg", "type": "string"},
                        {"contentEncoding": "base64", "contentMediaType": "image/png", "type": "string"},
                    ]
                },
                "title": "Output image which is the result of the mathematical " "expressions on input image list operands.",
            }
        },
        "outputTransmission": ["value", "reference"],
    }


@pytest.fixture
def mock_collections_data_2():
    return {
        "id": "hellor",
        "version": "2.0.0",
        "title": "HelloWorld Service in R",
        "description": ("Output and Hello Wolrd string"),
        "inputs": {
            "S": {"description": "The name to display in the hello message", "schema": {"type": "string"}, "title": "Name"}
        },
        "outputs": {
            "Result": {
                "description": "The string created by service.",
                "schema": {"type": "string"},
                "title": "The resulting string",
            }
        },
        "outputTransmission": ["value", "reference"],
    }


@pytest.fixture
def mock_api_data():
    return {"paths": {}}


def test_get_collections_success(mock_collections_data):
    with requests_mock.Mocker() as m:
        url = "https://ospd.geolabs.fr:8300/ogc-api/processes/OTB.BandMath"
        m.get(url, json=mock_collections_data)

        init = Initialize()
        result = init.get_collections(url)

        assert result == mock_collections_data


def test_get_collections_failure():
    with requests_mock.Mocker() as m:
        url = "https://ospd.geolabs.fr:8300/ogc-api/processes/securityOut"
        m.get(url, status_code=500)

        init = Initialize()
        result = init.get_collections(url)

        assert result is None


def test_json_to_galaxyxml(mock_collections_data_2, mock_api_data):
    init = Initialize()

    expected_xml = """
    <tool name="hellor" id="hellor" version="@TOOL_VERSION@+galaxy@VERSION_SUFFIX@">
  <description>HelloWorld Service in R</description>
  <macros>
    <import>Macros/hellor_macros_.xml</import>
  </macros>
  <requirements>
    <requirement version="3.10.12" type="package">python</requirement>
    <requirement version="2.31.0" type="package">requests</requirement>
  </requirements>
  <version_command><![CDATA[interpreter filename.exe --version]]></version_command>
  <command><![CDATA[$__tool_directory__/Code/openapi.py output_data_Result $output_data_Result  name hellor S '$S'
prefer $Section_prefer.prefer
response $Section_response.response
transmissionMode_Result $OutputSection_Result.transmissionMode_Result]]></command>
  <inputs>
    <param name="S" type="text" optional="false" label="S" help="Name The name to display in the hello message">
      <validator type="empty_field"/>
    </param>
    <section name="Section_prefer" title="Choose the prefer" expanded="true" help="Choose between 'return=representation', 'return=minimal', and 'respond-async;return=representation'.The specification is for synchronous or asynchronous executions,with asynchronous execution as the default value">
      <param name="prefer" type="select" label="Prefer">
        <option selected="true" value="respond-async;return=representation">respond-async;return=representation</option>
        <option value="return=minimal">return=minimal</option>
        <option value="return=representation">return=representation</option>
      </param>
    </section>
    <section name="Section_response" title="Choose the response type" expanded="true" help="Choose 'raw' to get the raw data or 'document' for retrieving a URL. The URL can be used for workflows, while the raw data is the download of the URL">
      <param name="response" type="select" label="Response Type" help="Choose 'raw' for raw data or 'document' for document data.">
        <option selected="true" value="document">document</option>
        <option value="raw">raw</option>
      </param>
    </section>
    <section name="OutputSection_Result" title="Select the appropriate transmission mode for Result" expanded="true">
      <param name="transmissionMode_Result" type="select" label="Choose the transmission mode">
        <option selected="true" value="reference">reference</option>
        <option value="value">value</option>
      </param>
    </section>
  </inputs>
  <outputs>
    <data name="output_data_Result" format="txt" label="Result" hidden="false"/>
  </outputs>
  <tests>
    <test>
      <param name="response" value="document"/>
      <output name="output_data_Result" ftype="txt" value="output_data_Result.txt"/>
    </test>
  </tests>
  <help><![CDATA[Output and Hello Wolrd string]]></help>
  <citations>
    <citation type="bibtex">Josh</citation>
  </citations>
</tool>
    """.strip()

    # Mock the open function and the file handle
    # Mock the open function and the file handle
    with patch("builtins.open", mock_open()) as mock_open_function, patch(
        "GeneratorXML.galaxyxml_creator.Galaxyxmltool"
    ) as mock_galaxyxmltool:

        mock_file_handle = mock_open_function.return_value
        mock_galaxyxmltool_instance = mock_galaxyxmltool.return_value
        mock_galaxyxmltool_instance.get_tool.return_value.export.return_value = expected_xml

        # Call your method that writes XML
        init.json_to_galaxyxml(process_data=mock_collections_data_2, api_data=mock_api_data)

        # Assert that open was called with the correct file path and write was called with the expected XML
        mock_open_function.assert_called_with(f"Tools/{mock_collections_data_2['id']}.xml", "w")
        written_xml = mock_file_handle.write.call_args[0][0].strip()  # Get the written XML and strip whitespace
        assert written_xml == expected_xml, f"Expected:\n{expected_xml}\n\nActual:\n{written_xml}"
