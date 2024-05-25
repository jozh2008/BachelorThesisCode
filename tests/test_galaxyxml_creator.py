import sys
import os

# Add the parent directory of galaxyxml_creator to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from galaxyxml_creator import Galaxyxmltool

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def setup_tool():
    name = "OTB.BandMath"
    id = "otb_bandmath"
    version = "1.0.0"
    description = "Outputs a monoband image which is the result of a mathematical operation on several multi-band images"

    tool = Galaxyxmltool(name=name, id=id, version=version, description=description)
    tool.gxtp = MagicMock()
    return tool


def test_create_text_param(setup_tool):
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
    assert param == tool.gxtp.TextParam.return_value
