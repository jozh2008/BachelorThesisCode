import sys
import os

# Add the parent directory of galaxyxml_creator to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from galaxyxml_creator import Galaxyxmltool

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def setup_tool():
    name = "OTB.BandMath"
    id = "otb_bandmath"
    version = "1.0.0"
    description = "Outputs a monoband image which is the result of a mathematical operation on several multi-band images"

    tool = Galaxyxmltool(name=name, id=id, version=version, description=description)
    tool.gxtp = MagicMock()
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
        optional=is_nullable,
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
        optional=is_nullable,
    )
    tool.gxtp.ValidatorParam.assert_called_with(name="validator", type="empty_field")
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
        name=f"select{param_name}",
        label=f"Do you want to add optional parameter {param_name}",
        help=description,
        options={"yes": "yes", "no": "no"},
        default="yes",
    )
    tool.gxtp.IntegerParam.assert_called_with(
        name=param_name,
        label=title,
        help=description,
        value=128,
        optional=is_nullable,
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
        optional=is_nullable,
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
        optional=is_nullable,
    )
    assert param == tool.gxtp.SelectParam.return_value


@patch("builtins.print")
def test_create_select_param_no_enum_values(mock_print, setup_tool):
    param_name = "test_param"
    param_dict = {
        "description": "Test Description",
        "schema": {},
        "title": "Test Title",
    }
    description = param_dict.get("description")
    title = param_dict.get("title")
    param_schema = param_dict.get("schema", {})
    is_nullable = True
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
        optional=is_nullable,
    )

    assert param == tool.gxtp.SelectParam.return_value
