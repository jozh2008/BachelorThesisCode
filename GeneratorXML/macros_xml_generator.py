import xml.etree.ElementTree as ET


class MacrosXMLGenerator:
    def __init__(self):
        self.root = ET.Element("macros")

    def add_token(self, name, value):
        """
        Add a token element to the XML root.

        Args:
            name (str): The name attribute of the token element.
            value (str): The text value of the token element.
        """
        token = ET.Element("token", {"name": name})
        token.text = value
        self.root.append(token)

    def generate_xml(self, filename):
        """
        Generate and write the XML tree to a file.

        Args:
            filename (str): The name of the file to write the XML data to.
        """
        tree = ET.ElementTree(self.root)
        tree.write(filename)

    def get_output_data(self, name, ftype):
        """
        Create an XML element structure for output data.

        Args:
            name (str): The name attribute of the output element.
            ftype (str): The ftype attribute of the output element.

        Returns:
            xml.etree.ElementTree.Element: An XML element representing the output data structure.
        """
        # Create the output structure
        output_element = ET.Element("output", {"name": f"{name}", "ftype": ftype})
        assert_contents = ET.SubElement(output_element, "assert_contents")
        ET.SubElement(assert_contents, "has_n_lines", {"n": "1"})

        return output_element

    def create_macro_file(self, filename, name, ftype, macro_name):
        """
        Create or update an XML file with a macro element containing output data.

        Args:
            filename (str): The name of the XML file to read and write.
            name (str): The name attribute of the output element within the macro.
            ftype (str): The ftype attribute of the output element within the macro.
            macro_name (str): The name attribute of the macro element.
        """

        tree = ET.parse(filename)
        root = tree.getroot()

        # Create the macro element with the required output
        macro_element = ET.Element("xml", {"name": f"{macro_name}"})
        output_element = self.get_output_data(name=name, ftype=ftype)
        macro_element.append(output_element)

        # Append the new macro element to the root or to an appropriate location
        root.append(macro_element)

        tree.write(filename)
