import pytest
import requests_mock

from unittest.mock import patch, mock_open, MagicMock
from main import GalaxyToolConverter, main


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
                                            {
                                                "contentEncoding": "base64",
                                                "contentMediaType": "image/tiff",
                                                "type": "string",
                                            },
                                            {
                                                "contentEncoding": "base64",
                                                "contentMediaType": "image/jpeg",
                                                "type": "string",
                                            },
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


@pytest.fixture
def mock_galaxy_tool_converter():
    with patch("main.GalaxyToolConverter") as MockGalaxyToolConverter:
        instance = MockGalaxyToolConverter.return_value
        instance.retrieve_json.side_effect = [
            {"data": "collections_data"},  # Mock return for first call
            {"data": "api_data"},  # Mock return for second call
        ]
        instance.json_to_galaxyxml = MagicMock()
        yield instance


def test_get_collections_success(mock_collections_data):
    with requests_mock.Mocker() as m:
        url = "https://ospd.geolabs.fr:8300/ogc-api/processes/OTB.BandMath"
        m.get(url, json=mock_collections_data)

        init = GalaxyToolConverter()
        result = init.retrieve_json(url)

        assert result == mock_collections_data


def test_get_collections_failure():
    with requests_mock.Mocker() as m:
        url = "https://ospd.geolabs.fr:8300/ogc-api/processes/securityOut"
        m.get(url, status_code=500)

        init = GalaxyToolConverter()
        result = init.retrieve_json(url)

        assert result is None


def test_json_to_galaxyxml(mock_collections_data_2, mock_api_data):
    init = GalaxyToolConverter()

    expected_xml = (
        '<tool name="hellor" id="hellor" version="@TOOL_VERSION@+galaxy@VERSION_SUFFIX@">\n'
        "  <description>HelloWorld Service in R</description>\n"
        "  <macros>\n"
        "    <import>Macros/hellor_macros_.xml</import>\n"
        "  </macros>\n"
        "  <requirements>\n"
        '    <requirement version="3.10.12" type="package">python</requirement>\n'
        '    <requirement version="2.31.0" type="package">requests</requirement>\n'
        "  </requirements>\n"
        "  <version_command><![CDATA[interpreter filename.exe --version]]></version_command>\n"
        "  <command><![CDATA[$__tool_directory__/Code/create_api_json.py output_data_Result $output_data_Result  name hellor S "
        "'$S'\n"
        "prefer $Section_prefer.prefer\n"
        "response $Section_response.response\n"
        "transmissionMode_Result $OutputSection_Result.transmissionMode_Result]]></command>\n"
        "  <inputs>\n"
        '    <param name="S" type="text" optional="false" label="S" help="Name The name to display in the hello message">\n'
        '      <validator type="empty_field"/>\n'
        "    </param>\n"
        '    <section name="Section_prefer" title="Choose the prefer" expanded="true" help="Choose between '
        "'return=representation', 'return=minimal', and 'respond-async;return=representation'."
        'The specification is for synchronous or asynchronous executions, with synchronous execution as the default value">\n'
        '      <param name="prefer" type="select" label="Prefer">\n'
        '        <option value="respond-async;return=representation">'
        "respond-async;return=representation</option>\n"
        '        <option value="return=minimal">return=minimal</option>\n'
        '        <option selected="true" value="return=representation">return=representation</option>\n'
        "      </param>\n"
        "    </section>\n"
        '    <section name="Section_response" title="Choose the response type" expanded="true" help="Choose '
        "'raw' to get the raw data or 'document' for retrieving a URL. "
        "The URL can be used for workflows, while the raw data is the download of the URL"
        '">\n'
        '      <param name="response" type="select" label="Response Type" help="Choose '
        "'raw' for raw data or 'document' for document data.\">\n"
        '        <option selected="true" value="document">document</option>\n'
        '        <option value="raw">raw</option>\n'
        "      </param>\n"
        "    </section>\n"
        '    <section name="OutputSection_Result" title="Select the appropriate transmission mode for Result" expanded="true">\n'
        '      <param name="transmissionMode_Result" type="select" label="Choose the transmission mode">\n'
        '        <option selected="true" value="reference">reference</option>\n'
        '        <option value="value">value</option>\n'
        "      </param>\n"
        "    </section>\n"
        "  </inputs>\n"
        "  <outputs>\n"
        '    <data name="output_data_Result" format="txt" label="output_data_Result" hidden="false"/>\n'
        "  </outputs>\n"
        "  <tests>\n"
        "    <test>\n"
        '      <param name="response" value="document"/>\n'
        '      <output name="output_data_Result" ftype="txt" value="output_data_Result.txt"/>\n'
        "    </test>\n"
        "  </tests>\n"
        "  <help><![CDATA[Output and Hello Wolrd string]]></help>\n"
        "  <citations>\n"
        '    <citation type="bibtex">.</citation>\n'
        "  </citations>\n"
        "</tool>"
    ).strip()

    # Mock the open function and the file handle
    with patch("builtins.open", mock_open()) as mock_open_function, patch(
        "GeneratorXML.galaxyxml_creator.GalaxyXmlTool"
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


def test_main(mock_galaxy_tool_converter):
    base_url = "https://ospd.geolabs.fr:8300/ogc-api/"
    process_name = "OTB.BandMath"

    main(base_url, process_name)

    # Assertions
    mock_galaxy_tool_converter.retrieve_json.assert_any_call(url=f"{base_url}processes/{process_name}")
    mock_galaxy_tool_converter.retrieve_json.assert_any_call(url=f"{base_url}api")
    mock_galaxy_tool_converter.json_to_galaxyxml.assert_called_once_with(
        process_data={"data": "collections_data"}, api_data={"data": "api_data"}
    )
