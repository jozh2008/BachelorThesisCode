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
