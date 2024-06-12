import os
import sys
import math
import pytest

# from pprint import pprint
from unittest.mock import MagicMock, patch


# Add the parent directory of galaxyxml_creator to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from galaxyxml_creator import Galaxyxmltool


@pytest.fixture
def setup_tool():
    name = "OTB.BandMath"
    id = "otb_bandmath"
    version = "1.0.0"
    description = "Outputs a monoband image which is the result of a mathematical operation on several multi-band images"

    tool = Galaxyxmltool(name=name, id=id, version=version, description=description)
    tool.gxtp = MagicMock()
    tool.output_type_dictionary = {}
    tool.output_name_list = []

    return tool


def test_create_text_param_nullable(setup_tool):
    param_name = "exp"
    param_dict = {
        "description": "The muParser mathematical expression to apply on input "
        "images.",
        "schema": {"type": "string", "nullable": True, "default": "im1b1+im1b2"},
        "title": "The muParser mathematical expression to apply on input images.",
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")

    tool = setup_tool

    param = tool.create_text_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        title=title,
        description=description,
    )
    tool.gxtp.TextParam.assert_called_with(
        name=param_name,
        label=title,
        help=description,
        value="im1b1+im1b2",
        optional=True,
    )
    assert param == tool.gxtp.TextParam.return_value


def test_create_text_param_nullable_false(setup_tool):
    param_name = "exp"
    param_dict = {
        "description": "The muParser mathematical expression to apply on input "
        "images.",
        "schema": {"type": "string"},
        "title": "The muParser mathematical expression to apply on input images.",
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")

    tool = setup_tool

    param = tool.create_text_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        title=title,
        description=description,
    )
    tool.gxtp.TextParam.assert_called_with(
        name=param_name,
        label=title,
        help=description,
        value=None,
        optional=False,
    )
    tool.gxtp.ValidatorParam.assert_called_with(name=None, type="empty_field")
    assert param.append.call_args_list == [((tool.gxtp.ValidatorParam.return_value,),)]


def test_create_integer_param_with_default_value_nullable(setup_tool):
    param_name = "ram"
    param_dict = {
        "description": "Available memory for processing (in MB)",
        "schema": {"default": 128, "nullable": True, "type": "integer"},
        "title": "Available memory for processing (in MB)",
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")

    tool = setup_tool

    param = tool.create_integer_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        title=title,
        description=description,
    )
    tool.gxtp.Conditional.assert_called_once()
    tool.gxtp.SelectParam.assert_called_with(
        name=f"select_{param_name}",
        label=f"Do you want to add optional parameter {param_name}?",
        help=description,
        options={"yes": "yes", "no": "no"},
        default="yes",
    )
    tool.gxtp.IntegerParam.assert_called_with(
        name=param_name,
        label=title,
        help=description,
        value=128,
        optional=True,
    )
    assert param == tool.gxtp.Conditional.return_value


def test_create_integer_param_with_default_value(setup_tool):
    param_name = "ram"
    param_dict = {
        "description": "Available memory for processing (in MB)",
        "schema": {"default": 128, "type": "integer"},
        "title": "Available memory for processing (in MB)",
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")

    tool = setup_tool

    param = tool.create_integer_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        title=title,
        description=description,
    )
    tool.gxtp.IntegerParam.assert_called_with(
        name=param_name, label=title, help=description, value=128
    )
    assert param == tool.gxtp.IntegerParam.return_value


def test_create_float_param_with_default_value(setup_tool):
    param_name = "wgt"
    param_dict = {
        "title": "Coefficient between 0 and 1 to promote undetection or false detections (default 0.5)",
        "description": "Coefficient between 0 and 1 to promote undetection or false detections (default 0.5)",
        "schema": {"type": "number", "default": 0.5, "format": "double"},
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")

    tool = setup_tool

    param = tool.create_float_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        title=title,
        description=description,
    )
    tool.gxtp.FloatParam.assert_called_with(
        name=param_name, label=title, help=description, value=0.5
    )
    assert param == tool.gxtp.FloatParam.return_value


def test_create_select_param_with_default_value(setup_tool):
    param_name = "out"
    param_dict = {
        "description": "Output image which is the result of the mathematical "
        "expressions on input image-list operands.",
        "schema": {
            "default": "float",
            "enum": ["uint8", "uint16", "int16", "int32", "float", "double"],
            "type": "string",
        },
        "title": "Output image which is the result of the mathematical expressions on "
        "input image-list operands.",
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_type_bool = False

    tool = setup_tool

    param = tool.create_select_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        param_type_bool=param_type_bool,
        title=title,
        description=description,
    )
    tool.gxtp.SelectParam.assert_called_with(
        name=param_name,
        default="float",
        label=title,
        help=description,
        options={
            "double": "double",
            "float": "float",
            "int16": "int16",
            "int32": "int32",
            "uint16": "uint16",
            "uint8": "uint8",
        },
        optional=False,
    )
    assert param == tool.gxtp.SelectParam.return_value


def test_create_select_param_boolean(setup_tool):
    param_name = "usenan"
    param_dict = {
        "description": "If active, the application will consider NaN as no-data "
        "values as well",
        "schema": {"default": False, "type": "boolean"},
        "title": "If active, the application will consider NaN as no-data values as "
        "well",
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_type_bool = True
    tool = setup_tool

    param = tool.create_select_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        param_type_bool=param_type_bool,
        title=title,
        description=description,
    )
    tool.gxtp.SelectParam.assert_called_with(
        name=param_name,
        default="false",
        label=title,
        help=description,
        options={"false": "false", "true": "true"},
        optional=False,
    )
    assert param == tool.gxtp.SelectParam.return_value


@patch("builtins.print")
def test_create_select_param_no_enum_values(mock_print, setup_tool):
    param_name = "test_param"
    param_dict = {
        "description": "Test Description",
        "schema": {"nullable": True},
        "title": "Test Title",
    }
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_schema = param_dict.get("schema", {})
    is_nullable = param_schema.get("nullable", False)
    param_type_bool = False

    tool = setup_tool

    param = tool.create_select_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        param_type_bool=param_type_bool,
        title=title,
        description=description,
    )

    mock_print.assert_called_once_with(
        "Warning: Enum values are not provided for select parameter. Implementation needed."
    )
    tool.gxtp.SelectParam.assert_called_with(
        name=param_name,
        default=None,
        label=title,
        help=description,
        options={},
        optional=True,
    )

    assert param == tool.gxtp.SelectParam.return_value


def test_create_data_param_is_array(setup_tool):
    param_name = "il"
    param_dict = {
        "description": "Image-list of operands to the mathematical expression.",
        "extended-schema": {
            "items": {
                "oneOf": [
                    {
                        "allOf": [
                            {"$ref": "http://zoo-project.org/dl/link.json"},
                            {
                                "properties": {
                                    "type": {
                                        "enum": [
                                            "image/tiff",
                                            "image/jpeg",
                                            "image/png",
                                        ]
                                    }
                                },
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
                                    {
                                        "contentEncoding": "base64",
                                        "contentMediaType": "image/png",
                                        "type": "string",
                                    },
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
                {
                    "contentEncoding": "base64",
                    "contentMediaType": "image/png",
                    "type": "string",
                },
            ]
        },
        "title": "Image-list of operands to the mathematical expression.",
    }
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_extended_schema = param_dict.get("extended-schema")
    tool = setup_tool
    is_nullable = param_extended_schema.get("nullable", False)
    is_array = param_extended_schema.get("type") == "array"

    param = tool.create_data_param(
        param_name=param_name,
        param_extended_schema=param_extended_schema,
        is_nullable=is_nullable,
        is_array=is_array,
        title=title,
        description=description,
    )
    tool.gxtp.DataParam.assert_called_with(
        name=param_name,
        label=title,
        help=f"{description} The following data types are allowed in the txt file: tiff, jpeg, png",
        format="txt",
        optional=is_nullable,
    )
    assert param == tool.gxtp.DataParam.return_value


def test_create_data_param_nullable(setup_tool):
    param_name = "b"
    param_dict = {
        "title": "Complex Input",
        "description": "A complex input ",
        "extended-schema": {
            "oneOf": [
                {
                    "allOf": [
                        {"$ref": "http://zoo-project.org/dl/link.json"},
                        {
                            "type": "object",
                            "properties": {
                                "type": {"enum": ["text/xml", "application/json"]}
                            },
                        },
                    ]
                },
                {
                    "type": "object",
                    "required": ["value"],
                    "properties": {
                        "value": {
                            "oneOf": [
                                {
                                    "type": "string",
                                    "contentEncoding": "utf-8",
                                    "contentMediaType": "text/xml",
                                },
                                {"type": "object"},
                            ]
                        }
                    },
                },
            ],
            "nullable": True,
        },
        "schema": {
            "oneOf": [
                {
                    "type": "string",
                    "contentEncoding": "utf-8",
                    "contentMediaType": "text/xml",
                },
                {"type": "object"},
            ]
        },
    }
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_extended_schema = param_dict.get("extended-schema")
    tool = setup_tool
    is_nullable = param_extended_schema.get("nullable", False)
    is_array = param_extended_schema.get("type") == "array"

    param = tool.create_data_param(
        param_name=param_name,
        param_extended_schema=param_extended_schema,
        is_nullable=is_nullable,
        is_array=is_array,
        title=title,
        description=description,
    )
    tool.gxtp.DataParam.assert_called_with(
        name="b",
        label="Complex Input",
        help=f"{description} The following data types are allowed in the txt file: xml, json",
        format="txt",
        optional=True,
    )
    assert param == tool.gxtp.DataParam.return_value


def test_create_data_param(setup_tool):
    param_name = "b"
    param_dict = {
        "title": "Complex Input",
        "description": "A complex input ",
        "extended-schema": {
            "oneOf": [
                {
                    "allOf": [
                        {"$ref": "http://zoo-project.org/dl/link.json"},
                        {
                            "type": "object",
                            "properties": {
                                "type": {"enum": ["text/xml", "application/json"]}
                            },
                        },
                    ]
                },
                {
                    "type": "object",
                    "required": ["value"],
                    "properties": {
                        "value": {
                            "oneOf": [
                                {
                                    "type": "string",
                                    "contentEncoding": "utf-8",
                                    "contentMediaType": "text/xml",
                                },
                                {"type": "object"},
                            ]
                        }
                    },
                },
            ],
        },
        "schema": {
            "oneOf": [
                {
                    "type": "string",
                    "contentEncoding": "utf-8",
                    "contentMediaType": "text/xml",
                },
                {"type": "object"},
            ]
        },
    }
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_extended_schema = param_dict.get("extended-schema")
    tool = setup_tool
    is_nullable = param_extended_schema.get("nullable", False)
    is_array = param_extended_schema.get("type") == "array"

    param = tool.create_data_param(
        param_name=param_name,
        param_extended_schema=param_extended_schema,
        is_nullable=is_nullable,
        is_array=is_array,
        title=title,
        description=description,
    )
    tool.gxtp.DataParam.assert_called_with(
        name="b",
        label="Complex Input",
        help=f"{description} The following data types are allowed in the txt file: xml, json",
        format="txt",
        optional=False,
    )
    assert param == tool.gxtp.DataParam.return_value


def test_create_object_param(setup_tool):
    param_name = "c"
    param_dict = {
        "description": "A boundingbox input ",
        "schema": {
            "nullable": True,
            "properties": {
                "bbox": {
                    "items": {"format": "double", "type": "number"},
                    "oneOf": [
                        {"maxItems": 4, "minItems": 4},
                        {"maxItems": 6, "minItems": 6},
                    ],
                    "type": "array",
                },
                "crs": {
                    "default": "urn:ogc:def:crs:EPSG:6.6:4326",
                    "enum": [
                        "urn:ogc:def:crs:EPSG:6.6:4326",
                        "urn:ogc:def:crs:EPSG:6.6:3785",
                    ],
                    "format": "uri",
                    "type": "string",
                },
            },
            "required": ["bbox", "crs"],
            "type": "object",
        },
        "title": "BoundingBox Input ",
    }
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_schema = param_dict.get("schema", {})
    is_nullable = param_schema.get("nullable", False)

    tool = setup_tool
    tool.create_array_param = MagicMock()
    section_mock = MagicMock()
    tool.create_section = MagicMock(return_value=section_mock)
    tool.get_array_items = MagicMock(return_value=(4, 6))

    result = tool.create_object_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        title=title,
        description=description,
    )

    # Assert create_section is called with the correct arguments
    tool.create_section.assert_called_once_with(
        name=param_name, title=title, description=description
    )

    # Assert SelectParam is called correctly for the string field
    tool.gxtp.SelectParam.assert_called_once_with(
        name="crs",
        default="urn:ogc:def:crs:EPSG:6.6:4326",
        options={
            "urn:ogc:def:crs:EPSG:6.6:4326": "urn:ogc:def:crs:EPSG:6.6:4326",
            "urn:ogc:def:crs:EPSG:6.6:3785": "urn:ogc:def:crs:EPSG:6.6:3785",
        },
        label="crs",
        help="",
        optional=is_nullable,
    )
    # Assert create_array_param is called correctly for the array field
    tool.create_array_param.assert_called_once_with(
        name="bbox",
        item_type="number",
        min_items=4,
        max_items=6,
        title=None,
        description=None,
        item_name="numberData",
    )

    # Assert the parameters are appended to the section
    section_mock.append.assert_any_call(tool.gxtp.SelectParam.return_value)
    section_mock.append.assert_any_call(tool.create_array_param.return_value)

    # Assert the returned value is the mocked section
    assert result == section_mock


def test_get_array_items(setup_tool):
    tool = setup_tool
    # Test case 1: Empty constraints
    schema = {"oneOf": []}
    assert tool.get_array_items(schema) == (math.inf, -math.inf)

    # Test case 2: Single constraint with minItems and maxItems
    schema = {"oneOf": [{"minItems": 2, "maxItems": 5}]}
    assert tool.get_array_items(schema) == (2, 5)

    # Test case 3: Multiple constraints
    schema = {"oneOf": [{"minItems": 1, "maxItems": 4}, {"minItems": 3, "maxItems": 6}]}
    assert tool.get_array_items(schema) == (1, 6)

    # Test case 4: Constraints with only minItems
    schema = {"oneOf": [{"minItems": 2}, {"minItems": 4}]}
    assert tool.get_array_items(schema) == (2, -math.inf)

    # Test case 5: Constraints with only maxItems
    schema = {"oneOf": [{"maxItems": 5}, {"maxItems": 7}]}
    assert tool.get_array_items(schema) == (math.inf, 7)

    # Test case 6: Constraints with minItems and one maxItems
    schema = {
        "oneOf": [{"minItems": 2}, {"minItems": 1, "maxItems": 3}, {"minItems": 4}]
    }
    assert tool.get_array_items(schema) == (1, 3)

    # Test case 7: Constraints with maxItems and no minItems
    schema = {"oneOf": [{"maxItems": 4}, {"maxItems": 2}, {"maxItems": 5}]}
    assert tool.get_array_items(schema) == (math.inf, 5)


def test_create_array_param_number(setup_tool):
    tool = setup_tool
    tool.create_float_param = MagicMock(return_value="float_param")

    param = tool.create_array_param(
        name="bbox",
        item_type="number",
        min_items=4,
        max_items=6,
        title=None,
        description=None,
        item_name="numberData",
    )
    tool.gxtp.Repeat.assert_called_once_with(
        name="bbox", title="Array item", min=4, max=6
    )

    # Assert create_float_param is called correctly
    tool.create_float_param.assert_called_once_with(
        param_name="floatData",
        param_schema=None,
        is_nullable=False,
        title=None,
        description=None,
    )

    # Assert the data is appended to the param
    tool.gxtp.Repeat.return_value.append.assert_called_once_with("float_param")

    # Assert the returned value is the Repeat mock
    assert param == tool.gxtp.Repeat.return_value


def test_create_array_param_integer(setup_tool):
    tool = setup_tool
    tool.create_integer_param = MagicMock(return_value="integer_param")

    param = tool.create_array_param(
        name="bbox",
        item_type="integer",
        min_items=4,
        max_items=6,
        title=None,
        description=None,
        item_name="integerData",
    )
    tool.gxtp.Repeat.assert_called_once_with(
        name="bbox", title="Array item", min=4, max=6
    )

    # Assert create_integer_param is called correctly
    tool.create_integer_param.assert_called_once_with(
        param_name="integerData",
        param_schema=None,
        is_nullable=False,
        title=None,
        description=None,
    )

    # Assert the data is appended to the param
    tool.gxtp.Repeat.return_value.append.assert_called_once_with("integer_param")

    # Assert the returned value is the Repeat mock
    assert param == tool.gxtp.Repeat.return_value


def test_create_array_param_string(setup_tool):
    tool = setup_tool
    tool.create_text_param = MagicMock(return_value="string_param")

    param = tool.create_array_param(
        name="bbox",
        item_type="string",
        min_items=4,
        max_items=6,
        title=None,
        description=None,
        item_name="stringData",
    )
    tool.gxtp.Repeat.assert_called_once_with(
        name="bbox", title="Array item", min=4, max=6
    )

    # Assert create_integer_param is called correctly
    tool.create_text_param.assert_called_once_with(
        param_name="stringData",
        param_schema=None,
        is_nullable=False,
        title=None,
        description=None,
    )

    # Assert the data is appended to the param
    tool.gxtp.Repeat.return_value.append.assert_called_once_with("string_param")

    # Assert the returned value is the Repeat mock
    assert param == tool.gxtp.Repeat.return_value


def test_create_section(setup_tool):
    tool = setup_tool
    section_name = "test_section"
    section_title = "Test Section"
    section_description = "This is a test section."

    section_mock = MagicMock()
    tool.gxtp.Section.return_value = section_mock

    result = tool.create_section(
        name=section_name, title=section_title, description=section_description
    )

    # Assert Section is called with the correct arguments
    tool.gxtp.Section.assert_called_once_with(
        name=section_name, title=section_title, help=section_description, expanded=True
    )

    # Assert the returned value is the mocked section
    assert result == section_mock


def test_create_select_raw_param(setup_tool):
    inputs = []
    tool = setup_tool
    section_mock = MagicMock()
    tool.create_section = MagicMock(return_value=section_mock)
    updated_inputs = tool.create_select_raw_param(inputs)

    # Assert that the create_section method was called with the correct parameters
    tool.create_section.assert_called_with(
        name="Section_response",
        title="Choose the response type",
        description=(
            "Choose 'raw' to get the raw data or 'document' for retrieving a URL. "
            "The URL can be used for workflows, while the raw data is the download of the URL"
        ),
    )

    # Assert that a SelectParam was created with the correct parameters
    tool.gxtp.SelectParam.assert_called_with(
        name="response",
        default="document",
        options={"raw": "raw", "document": "document"},
        label="Response Type",
        help="Choose 'raw' for raw data or 'document' for document data.",
    )

    # Assert the parameters are appended to the section
    section_mock.append.assert_any_call(tool.gxtp.SelectParam.return_value)

    # Assert that the section was added to the inputs
    assert section_mock in updated_inputs

    # Assert that the inputs list was modified correctly
    assert updated_inputs == inputs


def test_choose_prefer(setup_tool):
    inputs = []
    tool = setup_tool

    section_mock = MagicMock()
    tool.create_section = MagicMock(return_value=section_mock)
    updated_inputs = tool.choose_prefer(inputs)

    # Assert that the create_section method was called with the correct parameters
    tool.create_section.assert_called_with(
        name="Section_prefer",
        title="Choose the prefer",
        description=(
            "Choose between 'return=representation', 'return=minimal', and 'respond-async;return=representation'."
            "The specification is for synchronous or asynchronous executions,"
            "with asynchronous execution as the default value"
        ),
    )

    # Assert that a SelectParam was created with the correct parameters
    tool.gxtp.SelectParam.assert_called_with(
        name="prefer",
        default="respond-async;return=representation",
        options={
            "return=representation": "return=representation",
            "return=minimal": "return=minimal",
            "respond-async;return=representation": "respond-async;return=representation",
        },
        label="Prefer",
        help=None,
    )

    # Assert the parameters are appended to the section
    section_mock.append.assert_any_call(tool.gxtp.SelectParam.return_value)

    # Assert that the section was added to the inputs
    assert section_mock in updated_inputs

    # Assert that the inputs list was modified correctly
    assert updated_inputs == inputs


def test_choose_transmission_mode(setup_tool):
    name = "out"
    available_transmissions = ["value", "reference"]
    section = []
    tool = setup_tool

    section_mock = MagicMock()
    tool.create_section = MagicMock(return_value=section_mock)

    updated_section = tool.choose_transmission_mode(
        section, name, available_transmissions
    )

    # Assert that a SelectParam was created with the correct parameters
    tool.gxtp.SelectParam.assert_called_once_with(
        name="transmissionMode_out",
        default="reference",
        options={"value": "value", "reference": "reference"},
        label="Choose the transmission mode",
    )

    # Assert the parameters are appended to the section
    assert len(section) == 1
    assert section[0] == tool.gxtp.SelectParam.return_value

    # Assert that the section was added to the inputs
    assert updated_section == section


def test_create_output_param(setup_tool):

    tool = setup_tool

    tool.replace_dot_with_underscore = MagicMock(
        side_effect=lambda x: x.replace(".", "_")
    )
    mock_enum_values = ["image/tiff", "image/jpeg", "image/png"]
    tool.process_output_param = MagicMock(return_value=(MagicMock(), mock_enum_values))
    tool.create_section = MagicMock(return_value=MagicMock())
    tool.choose_transmission_mode = MagicMock()

    output_schema = {
        "out": {
            "description": "Output image which is the result of the mathematical "
            "expressions on input image-list operands.",
            "extended-schema": {
                "oneOf": [
                    {
                        "allOf": [
                            {"$ref": "http://zoo-project.org/dl/link.json"},
                            {
                                "properties": {
                                    "type": {
                                        "enum": [
                                            "image/tiff",
                                            "image/jpeg",
                                            "image/png",
                                        ]
                                    }
                                },
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
                                    {
                                        "contentEncoding": "base64",
                                        "contentMediaType": "image/png",
                                        "type": "string",
                                    },
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
                    {
                        "contentEncoding": "base64",
                        "contentMediaType": "image/png",
                        "type": "string",
                    },
                ]
            },
            "title": "Output image which is the result of the mathematical "
            "expressions on input image-list operands.",
        }
    }
    transmission_schema = ["value", "reference"]

    inputs = []
    tool.create_output_param(output_schema, inputs, transmission_schema)

    # Verify that replace_dot_with_underscore was called
    tool.replace_dot_with_underscore.assert_called_once_with("out")

    # Verify that process_output_param was called with the correct arguments
    tool.process_output_param.assert_called_once_with(
        output_param_name="outputType_out",
        param_extended_schema={
            "oneOf": [
                {
                    "allOf": [
                        {"$ref": "http://zoo-project.org/dl/link.json"},
                        {
                            "properties": {
                                "type": {
                                    "enum": ["image/tiff", "image/jpeg", "image/png"]
                                }
                            },
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
                                {
                                    "contentEncoding": "base64",
                                    "contentMediaType": "image/png",
                                    "type": "string",
                                },
                            ]
                        }
                    },
                    "required": ["value"],
                    "type": "object",
                },
            ]
        },
        param_schema={
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
                {
                    "contentEncoding": "base64",
                    "contentMediaType": "image/png",
                    "type": "string",
                },
            ]
        },
        param_type=None,
        enum_values=[],
        title="out",
        description="Output image which is the result of the mathematical expressions on input image-list operands.",
    )

    # Verify that create_section was called with the correct arguments
    tool.create_section.assert_called_once_with(
        name="OutputSection_out",
        title="Select the appropriate transmission mode for out and specify an output format",
    )

    # Verify that choose_transmission_mode was called with the correct arguments
    tool.choose_transmission_mode.assert_called_once_with(
        tool.create_section.return_value,
        name="out",
        available_transmissions=transmission_schema,
    )

    # Verify that the section was appended to inputs
    assert tool.create_section.return_value in inputs
    assert len(inputs) == 1

    # Verify the updates to output_type_dictionary and output_name_list
    assert tool.output_type_dictionary == {
        "outputType_out": ["image/tiff", "image/jpeg", "image/png"]
    }
    assert tool.output_name_list == ["out"]


def test_create_process_output_param(setup_tool):
    tool = setup_tool

    mock = MagicMock()
    tool.create_select_param_output = MagicMock(return_value=mock)

    output_schema = {
        "out": {
            "description": "Output image which is the result of the mathematical "
            "expressions on input image-list operands.",
            "extended-schema": {
                "oneOf": [
                    {
                        "allOf": [
                            {"$ref": "http://zoo-project.org/dl/link.json"},
                            {
                                "properties": {
                                    "type": {
                                        "enum": [
                                            "image/tiff",
                                            "image/jpeg",
                                            "image/png",
                                        ]
                                    }
                                },
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
                                    {
                                        "contentEncoding": "base64",
                                        "contentMediaType": "image/png",
                                        "type": "string",
                                    },
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
                    {
                        "contentEncoding": "base64",
                        "contentMediaType": "image/png",
                        "type": "string",
                    },
                ]
            },
            "title": "Output image which is the result of the mathematical "
            "expressions on input image-list operands.",
        }
    }

    param, enum_values = tool.process_output_param(
        output_param_name="outputType_out",
        param_extended_schema=output_schema["out"]["extended-schema"],
        param_schema=output_schema["out"]["schema"],
        param_type=None,
        enum_values=[],
        title="out",
        description=output_schema["out"]["description"],
    )

    tool.create_select_param_output.assert_called_once_with(
        param_name="outputType_out",
        param_extended_schema={
            "oneOf": [
                {
                    "allOf": [
                        {"$ref": "http://zoo-project.org/dl/link.json"},
                        {
                            "properties": {
                                "type": {
                                    "enum": ["image/tiff", "image/jpeg", "image/png"]
                                }
                            },
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
                                {
                                    "contentEncoding": "base64",
                                    "contentMediaType": "image/png",
                                    "type": "string",
                                },
                            ]
                        }
                    },
                    "required": ["value"],
                    "type": "object",
                },
            ]
        },
        title="out",
        description=(
            "Output image which is the result of the mathematical "
            "expressions on input image-list operands."
        ),
    )
    assert enum_values == ["image/tiff", "image/jpeg", "image/png"]
    assert param == tool.create_select_param_output.return_value


def test_create_select_param_output(setup_tool):

    param_name = "outputType_out"
    param_extended_schema = (
        {
            "oneOf": [
                {
                    "allOf": [
                        {"$ref": "http://zoo-project.org/dl/link.json"},
                        {
                            "properties": {
                                "type": {
                                    "enum": ["image/tiff", "image/jpeg", "image/png"]
                                }
                            },
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
                                {
                                    "contentEncoding": "base64",
                                    "contentMediaType": "image/png",
                                    "type": "string",
                                },
                            ]
                        }
                    },
                    "required": ["value"],
                    "type": "object",
                },
            ]
        },
    )
    title = "out"
    description = (
        "Output image which is the result of the mathematical "
        "expressions on input image-list operands."
    )

    tool = setup_tool

    # Mock the extract_enum method to return the enum values
    tool.extract_enum = MagicMock()

    # Define the behavior of the MagicMock object
    def extract_enum_mock(schema_item=param_extended_schema, enum_values=[]):
        enum_values.extend(["image/tiff", "image/jpeg", "image/png"])

    # Assign the MagicMock object's side_effect to the defined behavior
    tool.extract_enum.side_effect = extract_enum_mock
    # enum_values = []

    result = tool.create_select_param_output(
        param_name=param_name,
        param_extended_schema=param_extended_schema,
        title=title,
        description=description,
    )
    tool.gxtp.SelectParam.assert_called_once_with(
        name="outputType_out",
        label="out",
        help=(
            "Output image which is the result of the mathematical "
            "expressions on input image-list operands."
        ),
        options={"image/jpeg": "jpeg", "image/png": "png", "image/tiff": "tiff"},
    )
    assert result == tool.gxtp.SelectParam.return_value
