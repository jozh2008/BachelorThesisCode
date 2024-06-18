import xml.etree.ElementTree as ET
import os
import pytest
import sys
from unittest.mock import patch, MagicMock


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from GeneratorXML.macros_xml_generator import MacrosXMLGenerator


@pytest.fixture
def mock_element_tree():
    # Mock ElementTree and related classes/methods
    mock_tree = MagicMock(spec=ET.ElementTree)
    mock_tree.write = MagicMock()
    return mock_tree


def test_add_token(mock_element_tree):
    generator = MacrosXMLGenerator()
    generator.root = ET.Element("macros")  # Reset root for clean test

    with patch.object(ET, "ElementTree", return_value=mock_element_tree):
        generator.add_token("token1", "value1")
        generator.add_token("token2", "value2")

        # Assertions
        assert len(generator.root.findall("token")) == 2
        assert generator.root.find('token[@name="token1"]').text == "value1"
        assert generator.root.find('token[@name="token2"]').text == "value2"


def test_generate_xml(mock_element_tree):
    generator = MacrosXMLGenerator()
    generator.root = ET.Element("macros")  # Reset root for clean test

    filename = "test.xml"

    with patch.object(ET, "ElementTree", return_value=mock_element_tree):
        generator.add_token("token1", "value1")
        generator.add_token("token2", "value2")
        generator.generate_xml(filename)

        # Assertions
        mock_element_tree.write.assert_called_once_with(filename)
