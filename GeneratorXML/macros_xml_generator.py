import xml.etree.ElementTree as ET


class MacrosXMLGenerator:
    def __init__(self):
        self.root = ET.Element("macros")

    def add_token(self, name, value):
        token = ET.Element("token", {"name": name})
        token.text = value
        self.root.append(token)

    def generate_xml(self, filename):
        tree = ET.ElementTree(self.root)
        tree.write(filename)

    def get_output_data(self, name, ftype):
        # Create the output structure
        output_element = ET.Element("output", {"name": f"{name}", "ftype": ftype})
        assert_contents = ET.SubElement(output_element, "assert_contents")
        ET.SubElement(assert_contents, "has_n_lines", {"n": "1"})

        return output_element

    def create_macro_file(self, filename, name, ftype, macro_name):
        tree = ET.parse(filename)
        root = tree.getroot()

        # Create the macro element with the required output
        macro_element = ET.Element("xml", {"name": f"{macro_name}"})
        output_element = self.get_output_data(name=name, ftype=ftype)
        macro_element.append(output_element)

        # Append the new macro element to the root or to an appropriate location
        root.append(macro_element)

        tree.write(filename)
