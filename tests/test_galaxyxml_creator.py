import math
import pytest

# from pprint import pprint
from unittest.mock import MagicMock, patch

from GeneratorXML.galaxyxml_creator import GalaxyXmlTool


@pytest.fixture
def setup_tool():
    name = "OTB.BandMath"
    id = "otb_bandmath"
    version = "1.0.0"
    description = "Outputs a monoband image which is the result of a mathematical operation on several multi-band images"

    tool = GalaxyXmlTool(name=name, id=id, version=version, description=description)
    tool.gxtp = MagicMock()

    tool.executable = "test_executable"
    tool.executable_dict = {}

    tool.gxtp.Inputs = MagicMock()
    tool.gxtp.Inputs.return_value.params = []

    tool.gxtp.Inputs.return_value.append.side_effect = lambda param: tool.gxtp.Inputs.return_value.params.append(param)

    return tool


def test_create_text_param_nullable(setup_tool):
    param_name = "exp"
    param_dict = {
        "description": "The muParser mathematical expression to apply on input " "images.",
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
        "description": "The muParser mathematical expression to apply on input " "images.",
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
    tool.gxtp.IntegerParam.assert_called_with(name=param_name, label=title, help=description, value=128)
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
    tool.gxtp.FloatParam.assert_called_with(name=param_name, label=title, help=description, value=0.5)
    assert param == tool.gxtp.FloatParam.return_value


def test_create_float_param_with_default_value_nullable(setup_tool):
    param_name = "wgt"
    param_dict = {
        "title": "Coefficient between 0 and 1 to promote undetection or false detections (default 0.5)",
        "description": "Coefficient between 0 and 1 to promote undetection or false detections (default 0.5)",
        "schema": {
            "type": "number",
            "default": 0.5,
            "format": "double",
            "nullable": True,
        },
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
    tool.gxtp.Conditional.assert_called_once()
    tool.gxtp.SelectParam.assert_called_with(
        name=f"select_{param_name}",
        label=f"Do you want to add optional parameter {param_name}?",
        help=description,
        options={"yes": "yes", "no": "no"},
        default="yes",
    )
    tool.gxtp.FloatParam.assert_called_with(
        name=param_name,
        label=title,
        help=description,
        value=0.5,
        optional=True,
    )
    assert param == tool.gxtp.Conditional.return_value


def test_create_select_param_with_default_value(setup_tool):
    param_name = "out"
    param_dict = {
        "description": "Output image which is the result of the mathematical " "expressions on input image-list operands.",
        "schema": {
            "default": "float",
            "enum": ["uint8", "uint16", "int16", "int32", "float", "double"],
            "type": "string",
        },
        "title": "Output image which is the result of the mathematical expressions on " "input image-list operands.",
    }
    param_schema = param_dict.get("schema")
    is_nullable = param_schema.get("nullable", False)
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_type_bool = False

    tool = setup_tool
    tool.remove_duplicate = MagicMock(side_effect=lambda x: list(dict.fromkeys(x)))

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
        "description": "If active, the application will consider NaN as no-data " "values as well",
        "schema": {"default": False, "type": "boolean"},
        "title": "If active, the application will consider NaN as no-data values as " "well",
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

    mock_print.assert_called_once_with("Warning: Enum values are not provided for select parameter. Implementation needed.")
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
                            "properties": {"type": {"enum": ["text/xml", "application/json"]}},
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
                            "properties": {"type": {"enum": ["text/xml", "application/json"]}},
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
    tool.remove_duplicate = MagicMock(side_effect=lambda x: list(dict.fromkeys(x)))

    result = tool.create_object_param(
        param_name=param_name,
        param_schema=param_schema,
        is_nullable=is_nullable,
        title=title,
        description=description,
    )

    # Assert create_section is called with the correct arguments
    tool.create_section.assert_called_once_with(name=param_name, title=title, description=description)

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
    schema = {"oneOf": [{"minItems": 2}, {"minItems": 1, "maxItems": 3}, {"minItems": 4}]}
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
    tool.gxtp.Repeat.assert_called_once_with(name="bbox", title="Array item", min=4, max=6)

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
    tool.gxtp.Repeat.assert_called_once_with(name="bbox", title="Array item", min=4, max=6)

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
    tool.gxtp.Repeat.assert_called_once_with(name="bbox", title="Array item", min=4, max=6)

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

    result = tool.create_section(name=section_name, title=section_title, description=section_description)

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
            "with synchronous execution as the default value"
        ),
    )

    # Assert that a SelectParam was created with the correct parameters
    tool.gxtp.SelectParam.assert_called_with(
        name="prefer",
        default="return=representation",
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

    updated_section = tool.choose_transmission_mode(section, name, available_transmissions)

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

    tool.replace_dot_with_underscore = MagicMock(side_effect=lambda x: x.replace(".", "_"))
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
            "title": "Output image which is the result of the mathematical " "expressions on input image-list operands.",
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
    assert tool.output_type_dictionary == {"outputType_out": ["image/tiff", "image/jpeg", "image/png"]}
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
            "title": "Output image which is the result of the mathematical " "expressions on input image-list operands.",
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
        description=("Output image which is the result of the mathematical " "expressions on input image-list operands."),
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
    description = "Output image which is the result of the mathematical " "expressions on input image-list operands."

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
        help=("Output image which is the result of the mathematical " "expressions on input image-list operands."),
        options={"image/jpeg": "jpeg", "image/png": "png", "image/tiff": "tiff"},
    )
    assert result == tool.gxtp.SelectParam.return_value


def test_create_params(setup_tool):
    tool = setup_tool

    tool.create_select_param = MagicMock()
    tool.create_text_param = MagicMock()
    tool.create_integer_param = MagicMock()
    tool.create_data_param = MagicMock()
    tool.choose_prefer = MagicMock()
    tool.create_select_raw_param = MagicMock()
    tool.create_output_param = MagicMock()
    input_schema = {
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
            "title": "Image list of operands to the mathematical expression.",
        },
        "out": {
            "description": "Output image which is the result of the mathematical "
            "expressions on input image list operands.",
            "schema": {
                "default": "float",
                "enum": ["uint8", "uint16", "int16", "int32", "float", "double"],
                "type": "string",
            },
            "title": "Output image which is the result of the mathematical " "expressions on input image list operands.",
        },
        "ram": {
            "description": "Available memory for processing (in MB).",
            "schema": {"default": 256, "nullable": True, "type": "integer"},
            "title": "Available memory for processing (in MB).",
        },
    }
    output_schema = {
        "out": {
            "description": "Output image which is the result of the mathematical "
            "expressions on input image list operands.",
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
            "title": "Output image which is the result of the mathematical " "expressions on input image list operands.",
        }
    }

    transmission_schema = ["value", "reference"]

    results = tool.create_params(input_schema, output_schema, transmission_schema)

    tool.create_text_param.assert_called_once_with(
        param_name="exp",
        param_schema={"type": "string"},
        is_nullable=False,
        title="exp",
        description="The muParser mathematical expression to apply on input images.",
    )
    tool.create_integer_param.assert_called_once_with(
        param_name="ram",
        param_schema={"default": 256, "nullable": True, "type": "integer"},
        is_nullable=True,
        title="ram",
        description="Available memory for processing (in MB).",
    )

    tool.create_select_param.assert_called_once_with(
        param_name="out",
        param_schema={
            "default": "float",
            "enum": ["uint8", "uint16", "int16", "int32", "float", "double"],
            "type": "string",
        },
        is_nullable=False,
        param_type_bool=False,
        title="out",
        description="Output image which is the result of the mathematical expressions on input image list operands.",
    )

    tool.create_data_param.assert_called_once_with(
        param_name="il",
        param_extended_schema={
            "type": "array",
            "minItems": 1,
            "maxItems": 1024,
            "items": {
                "oneOf": [
                    {
                        "allOf": [
                            {"$ref": "http://zoo-project.org/dl/link.json"},
                            {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "enum": [
                                            "image/tiff",
                                            "image/jpeg",
                                            "image/png",
                                        ]
                                    }
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
                                        "contentEncoding": "base64",
                                        "contentMediaType": "image/tiff",
                                    },
                                    {
                                        "type": "string",
                                        "contentEncoding": "base64",
                                        "contentMediaType": "image/jpeg",
                                    },
                                    {
                                        "type": "string",
                                        "contentEncoding": "base64",
                                        "contentMediaType": "image/png",
                                    },
                                ]
                            }
                        },
                    },
                ]
            },
        },
        is_nullable=False,
        is_array=True,
        title="il",
        description="Image list of operands to the mathematical expression.",
    )
    tool.choose_prefer.assert_called_once_with(inputs=results)

    tool.create_select_raw_param.assert_called_once_with(inputs=results)

    # Verify that create_output_param was called with the correct arguments
    tool.create_output_param.assert_called_once_with(
        output_schema=output_schema,
        inputs=results,
        transmission_schema=transmission_schema,
    )


def test_create_params_2(setup_tool):
    tool = setup_tool

    tool.create_select_param = MagicMock()
    tool.create_text_param = MagicMock()
    tool.create_float_param = MagicMock()
    tool.create_data_param = MagicMock()
    tool.create_object_param = MagicMock()
    tool.choose_prefer = MagicMock()
    tool.create_select_raw_param = MagicMock()
    tool.create_output_param = MagicMock()

    input_schema = {
        "a": {
            "description": "An input string",
            "schema": {"nullable": True, "type": "string"},
            "title": "Literal Input (string)",
        },
        "b": {
            "description": "A complex input ",
            "extended-schema": {
                "nullable": True,
                "oneOf": [
                    {
                        "allOf": [
                            {"$ref": "http://zoo-project.org/dl/link.json"},
                            {
                                "properties": {"type": {"enum": ["text/xml", "application/json"]}},
                                "type": "object",
                            },
                        ]
                    },
                    {
                        "properties": {
                            "value": {
                                "oneOf": [
                                    {
                                        "contentEncoding": "utf-8",
                                        "contentMediaType": "text/xml",
                                        "type": "string",
                                    },
                                    {"type": "object"},
                                ]
                            }
                        },
                        "required": ["value"],
                        "type": "object",
                    },
                ],
            },
            "schema": {
                "oneOf": [
                    {
                        "contentEncoding": "utf-8",
                        "contentMediaType": "text/xml",
                        "type": "string",
                    },
                    {"type": "object"},
                ]
            },
            "title": "Complex Input",
        },
        "c": {
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
        },
        "pause": {
            "description": "An optional input which can be used to specify the "
            "number of seconds to pause the service before "
            "returning",
            "schema": {
                "default": 10.0,
                "format": "double",
                "nullable": True,
                "type": "number",
            },
            "title": "Literal Input (double)",
        },
        "MATCH": {
            "title": "Match Fields by Name",
            "description": "Match Fields by Name",
            "schema": {"type": "boolean", "default": False, "enum": ["true", "false"], "nullable": True},
        },
    }

    output_schema = {
        "a": {
            "description": "The output a returned",
            "schema": {"type": "string"},
            "title": "The output a",
        },
        "b": {
            "description": "The output b returned",
            "extended-schema": {
                "oneOf": [
                    {
                        "allOf": [
                            {"$ref": "http://zoo-project.org/dl/link.json"},
                            {
                                "properties": {"type": {"enum": ["text/xml", "application/json"]}},
                                "type": "object",
                            },
                        ]
                    },
                    {
                        "properties": {
                            "value": {
                                "oneOf": [
                                    {
                                        "contentEncoding": "utf-8",
                                        "contentMediaType": "text/xml",
                                        "type": "string",
                                    },
                                    {"type": "object"},
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
                        "contentEncoding": "utf-8",
                        "contentMediaType": "text/xml",
                        "type": "string",
                    },
                    {"type": "object"},
                ]
            },
            "title": "The output b",
        },
        "c": {
            "description": "A boundingbox output ",
            "schema": {
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
            "title": "BoundingBox output ",
        },
    }
    transmission_schema = ["value", "reference"]
    results = tool.create_params(input_schema, output_schema, transmission_schema)

    tool.create_text_param.assert_called_once_with(
        param_name="a",
        param_schema={"nullable": True, "type": "string"},
        is_nullable=True,
        title="a",
        description="Literal Input (string) An input string",
    )

    tool.create_data_param.assert_called_once_with(
        param_name="b",
        param_extended_schema={
            "nullable": True,
            "oneOf": [
                {
                    "allOf": [
                        {"$ref": "http://zoo-project.org/dl/link.json"},
                        {
                            "properties": {"type": {"enum": ["text/xml", "application/json"]}},
                            "type": "object",
                        },
                    ]
                },
                {
                    "properties": {
                        "value": {
                            "oneOf": [
                                {
                                    "contentEncoding": "utf-8",
                                    "contentMediaType": "text/xml",
                                    "type": "string",
                                },
                                {"type": "object"},
                            ]
                        }
                    },
                    "required": ["value"],
                    "type": "object",
                },
            ],
        },
        is_nullable=True,
        is_array=False,
        title="b",
        description="Complex Input A complex input ",
    )
    tool.create_object_param.assert_called_once_with(
        param_name="c",
        param_schema={
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
        is_nullable=True,
        title="c",
        description="BoundingBox Input  A boundingbox input ",
    )
    tool.create_float_param.assert_called_once_with(
        param_name="pause",
        param_schema={
            "default": 10.0,
            "format": "double",
            "nullable": True,
            "type": "number",
        },
        is_nullable=True,
        title="pause",
        description=(
            "Literal Input (double) An optional input which can be used to specify "
            "the number of seconds to pause the service before returning"
        ),
    )

    tool.create_select_param.assert_called_once_with(
        param_name="MATCH",
        param_schema={"type": "boolean", "default": False, "enum": ["true", "false"], "nullable": True},
        is_nullable=True,
        param_type_bool=True,
        title="MATCH",
        description="Match Fields by Name",
    )

    tool.choose_prefer.assert_called_once_with(inputs=results)

    tool.create_select_raw_param.assert_called_once_with(inputs=results)

    # Verify that create_output_param was called with the correct arguments
    tool.create_output_param.assert_called_once_with(
        output_schema=output_schema,
        inputs=results,
        transmission_schema=transmission_schema,
    )


def test_replace_dot_with_underscore(setup_tool):
    tool = setup_tool
    assert tool.replace_dot_with_underscore("example.test") == "example_test"
    assert tool.replace_dot_with_underscore("another.test.case") == "another_test_case"
    assert tool.replace_dot_with_underscore("no_dots_here") == "no_dots_here"
    assert tool.replace_dot_with_underscore("") == ""
    assert tool.replace_dot_with_underscore("only.one.dot.") == "only_one_dot_"


def test_merge_strings_with_duplicate(setup_tool):
    tool = setup_tool
    tool.remove_duplicate = MagicMock(side_effect=lambda x: list(dict.fromkeys(x)))
    enum_values = ["abc", "abc", " def", "ghi", " jkl", "mno"]
    merged_result = tool.merge_strings(enum_values)
    assert merged_result == ["abc", "abc, def", "ghi", "ghi, jkl", "mno"]


def test_remove_duplicate(setup_tool):

    tool = setup_tool

    # Test case 1: List with duplicates
    input_list_1 = ["a", "b", "a", "c", "b", "d", "a"]
    expected_output_1 = ["a", "b", "c", "d"]
    assert tool.remove_duplicate(input_list_1) == expected_output_1

    # Test case 2: List with no duplicates
    input_list_2 = ["x", "y", "z"]
    expected_output_2 = ["x", "y", "z"]
    assert tool.remove_duplicate(input_list_2) == expected_output_2

    # Test case 3: Empty list
    input_list_3 = []
    expected_output_3 = []
    assert tool.remove_duplicate(input_list_3) == expected_output_3

    # Test case 4: List with all duplicates
    input_list_4 = ["a", "a", "a", "a", "a"]
    expected_output_4 = ["a"]
    assert tool.remove_duplicate(input_list_4) == expected_output_4

    # Test case 5: List with mixed types
    input_list_5 = [1, "a", 2, "b", 1, "a"]
    expected_output_5 = [1, "a", 2, "b"]
    assert tool.remove_duplicate(input_list_5) == expected_output_5


def test_find_index(setup_tool):
    tool = setup_tool
    # Test case 1: Pattern found in string
    string_1 = "abcxyzabc"
    pattern_1 = "xyz"
    expected_output_1 = 6
    assert tool.find_index(string_1, pattern_1) == expected_output_1

    # Test case 2: Pattern not found in string
    string_2 = "abcdef"
    pattern_2 = "xyz"
    expected_output_2 = -1
    assert tool.find_index(string_2, pattern_2) == expected_output_2

    # Test case 3: Pattern at the beginning of string
    string_3 = "xyzabc"
    pattern_3 = "xyz"
    expected_output_3 = 3
    assert tool.find_index(string_3, pattern_3) == expected_output_3


def test_dict_to_string(setup_tool):
    tool = setup_tool
    # Test case 1: Dictionary with integer keys and values
    dictionary_1 = {1: 10, 2: 20, 3: 30}
    expected_output_1 = " 1 10  2 20  3 30"
    assert tool.dict_to_string(dictionary_1) == expected_output_1

    # Test case 2: Dictionary with string keys and values
    dictionary_2 = {"key1": "value1", "key2": "value2", "key3": "value3"}
    expected_output_2 = " key1 value1  key2 value2  key3 value3"
    assert tool.dict_to_string(dictionary_2) == expected_output_2

    # Test case 3: Empty dictionary
    dictionary_3 = {}
    expected_output_3 = ""
    assert tool.dict_to_string(dictionary_3) == expected_output_3


def test_define_command_with_title(setup_tool):
    tool = setup_tool
    # Test case 1: Basic command definition with title
    title = "test_command"
    expected_command = "test_executable name test_command"
    assert tool.define_command(title) == expected_command

    # Test case 2: Command definition with additional parameters
    tool.executable_dict["param1"] = "value1"
    tool.executable_dict["param2"] = "value2"
    expected_command = "test_executable name test_command  param1 value1  param2 value2"
    assert tool.define_command(title) == expected_command


def test_define_macro(setup_tool):
    tool = setup_tool

    # Create a mock generator
    mock_generator = MagicMock()
    # Use patch to replace MacrosXMLGenerator with our mock
    with patch("GeneratorXML.galaxyxml_creator.MacrosXMLGenerator", return_value=mock_generator):
        # Call the method to test
        tool.define_macro()

    # Check if add_token was called with correct arguments
    mock_generator.add_token.assert_any_call("@TOOL_VERSION@", "1.0.0")
    mock_generator.add_token.assert_any_call("@VERSION_SUFFIX@", "0")

    # Check if generate_xml was called with the correct filename
    expected_file_path = f"Tools/{tool.macros_file_name}"
    mock_generator.generate_xml.assert_called_once_with(filename=expected_file_path)


def test_define_tests_without_valid_examples(setup_tool):
    tool = setup_tool
    api_dict = {
        "test_dictionary": {
            "examples": [
                {
                    "response": "raw",
                    "inputs": {},
                    "outputs": {},
                }
            ]
        }
    }
    process = "0TB.BandMath"

    tests_mock = MagicMock()
    test_a_mock = MagicMock()
    tool.gxtp = MagicMock()
    tool.gxtp.Tests = MagicMock(return_value=tests_mock)
    tool.gxtp.Test = MagicMock(return_value=test_a_mock)
    tool.gxtp.TestParam = MagicMock()
    tool.gxtp.TestOutput = MagicMock()

    tool.output_name_list = ["test"]

    # Call the method under test
    result = tool.define_tests(api_dict, process)

    tool.gxtp.TestParam.assert_called_once_with(name="response", value="document")
    tool.gxtp.TestOutput.assert_called_once_with(name="output_data_test", ftype="txt", value="output_data_test.txt")

    # Assertions to verify the mocked behavior
    param = tool.gxtp.TestParam.return_value
    output = tool.gxtp.TestOutput.return_value

    test_a_mock.append.assert_any_call(param)
    test_a_mock.append.assert_any_call(output)

    tests_mock.append.assert_called_once_with(test_a_mock)

    test_instance = tool.gxtp.Tests.return_value

    assert result == test_instance


def test_add_test_response_param(setup_tool):
    tool = setup_tool

    # Create a real list to track params
    params_list = []

    # Create a mock Test object
    test = MagicMock()
    test.params = params_list  # Use the real list here

    # Mock the TestParam creation
    test_param = MagicMock()
    test_param.name = "response"
    test_param.value = "document"
    tool.gxtp.TestParam.return_value = test_param

    # Define the append behavior to add to the real list
    def append_side_effect(param):
        test.params.append(param)

    test.append.side_effect = append_side_effect

    # Call the method under test
    tool.add_test_response_param(test, "document")

    # Assertions to ensure the param was added to test.params
    assert len(test.params) == 1
    assert test.params[0].name == "response"
    assert test.params[0].value == "document"


def test_create_test_input_param(setup_tool):
    tool = setup_tool

    # Mock TestParam creation
    test_param = MagicMock()
    test_param.name = "key"
    test_param.value = "value"
    tool.gxtp.TestParam.return_value = test_param

    param = tool.create_test_input_param("key", {"href": "value"})

    # Assertions to check the correctness of the created TestParam
    assert param.name == "key"
    assert param.value == "value"


def test_process_test_output_params(setup_tool):
    tool = setup_tool

    # Mock outputs dictionary
    outputs = {
        "output1": {"format": {"mediaType": "application/json"}},
        "output2": {"format": {"mediaType": "image/png"}},
    }

    response = "raw"  # Mock response type

    test = tool.gxtp.Test()

    # Call the method under test
    tool.process_test_output_params(test, outputs, response)

    # Assertions to verify the behavior
    assert tool.gxtp.Test.return_value.append.call_count == len(outputs)

    # Verify each call argument (param) is of type TestOutput
    for call_args in tool.gxtp.Test.return_value.append.call_args_list:
        param = call_args[0][0]  # Extract the first argument passed to append
        assert isinstance(param, MagicMock)  # Ensure it's a TestOutput mock object


def test_create_tests(setup_tool):
    tool = setup_tool

    # Mock example data
    examples = [
        {
            "inputs": {
                "exp": "im1b1+im1b2",
                "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
                "out": "float",
                "ram": 256,
            },
            "outputs": {"out": {"format": {"mediaType": "image/tiff"}, "transmissionMode": "reference"}},
            "response": "document",
        },
        {
            "inputs": {
                "exp": "im1b3,im1b2,im1b1",
                "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
                "out": "float",
                "ram": 256,
            },
            "outputs": {"out": {"format": {"mediaType": "image/jpeg"}, "transmissionMode": "reference"}},
            "response": "raw",
        },
    ]

    # Mock necessary methods and classes
    tool.add_test_response_param = MagicMock()
    tool.process_test_input_params = MagicMock()
    tool.process_test_output_params = MagicMock()

    tool.gxtp.Test = MagicMock()
    tool.gxtp.Tests = MagicMock()

    # Call the method under test
    tests = tool.create_tests(examples)

    # Assertions
    assert isinstance(tests, MagicMock)  # Ensure tests object is created
    assert tool.gxtp.Tests.call_count == 1  # Verify Tests() constructor call count

    # Verify the number of tests appended to the tests object
    assert tool.gxtp.Test.call_count == len(examples)

    # Verify that add_test_response_param, process_test_input_params, and process_test_output_params were called for each example
    assert tool.add_test_response_param.call_count == len(examples)
    assert tool.process_test_input_params.call_count == len(examples)
    assert tool.process_test_output_params.call_count == len(examples)


def test_define_tests_with_valid_example(setup_tool):

    tool = setup_tool
    api_dict = {
        "test_dictionary": {
            "examples": [
                {
                    "inputs": {
                        "exp": "im1b1+im1b2",
                        "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
                        "out": "float",
                        "ram": 256,
                    },
                    "outputs": {"out": {"format": {"mediaType": "image/tiff"}, "transmissionMode": "reference"}},
                    "response": "document",
                },
                {
                    "inputs": {
                        "exp": "im1b3,im1b2,im1b1",
                        "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
                        "out": "float",
                        "ram": 256,
                    },
                    "outputs": {"out": {"format": {"mediaType": "image/jpeg"}, "transmissionMode": "reference"}},
                    "response": "raw",
                },
            ]
        }
    }
    process = "0TB.BandMath"

    example_list = [
        {
            "inputs": {
                "exp": "im1b1+im1b2",
                "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
                "out": "float",
                "ram": 256,
            },
            "outputs": {"out": {"format": {"mediaType": "image/tiff"}, "transmissionMode": "reference"}},
            "response": "document",
        },
        {
            "inputs": {
                "exp": "im1b3,im1b2,im1b1",
                "il": [{"href": "http://geolabs.fr/dl/Landsat8Extract1.tif"}],
                "out": "float",
                "ram": 256,
            },
            "outputs": {"out": {"format": {"mediaType": "image/jpeg"}, "transmissionMode": "reference"}},
            "response": "raw",
        },
    ]
    tool.get_test_dictionary = MagicMock()
    tool.get_test_examples = MagicMock()
    tool.create_tests = MagicMock()
    tool.create_tests.return_value = MagicMock()
    tool.get_test_examples.return_value = example_list
    tool.get_test_dictionary.return_value = api_dict

    tool.define_tests(api_dict, process)
    tool.get_test_dictionary.assert_called_once_with(api_dict=api_dict, process=process)
    tool.get_test_examples.assert_called_once_with(data=api_dict)
    tool.create_tests.assert_called_with(examples=example_list)
