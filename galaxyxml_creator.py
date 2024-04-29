from galaxyxml import tool
import galaxyxml.tool.parameters as gtpx

from pprint import pprint
from typing import Dict, List, Union
import re


class Galaxyxmltool:
    def __init__(self, name, id, version, description) -> None:
        self.executable = "$__tool_directory__/openapi.py"
        self.gxt = tool.Tool(name=name, id=id, version=version, description=description, executable="")
        self.gxtp = gtpx
        self.executable_dict = {}
        self.output_type_list = {}

    def get_tool(self):
        return self.gxt

    def create_text_param(self, param_name: str, param_dict: Dict, is_nullable: bool):
        """
        Create a text parameter.

        Args:
            param_name (str): The name of the parameter.
            param_dict (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.

        Returns:
            TextParam: The created text parameter.
        """
        default_value = param_dict["schema"].get("default")
        return self.gxtp.TextParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            value=default_value,
            optional=is_nullable
        )

    def create_select_param(self, param_name: str, param_dict: Dict, is_nullable: bool, param_type_bool :bool):
        """
        Create a select parameter.

        Args:
            param_name (str): The name of the parameter.
            param_dict (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.

        Returns:
            SelectParam: The created select parameter.
        """
        enum_values = param_dict["schema"].get("enum")
        if enum_values is not None:
            options = {self.normalize_tool_name(value): value for value in enum_values}
        elif param_type_bool:
            options = {"true": "true", "false": "false"}
        else:
            # If enum values are not provided, handle this case gracefully
            print("Warning: Enum values are not provided for select parameter. Implementation needed.")
            options = {}  # Placeholder for options
        
        default_value = (param_dict["schema"].get("default"))

        if default_value is not None and param_type_bool:
            default_value = self.create_default_value(default_value=default_value)
        
        default_value = self.normalize_tool_name(tool_name=default_value)
        return self.gxtp.SelectParam(
            name=param_name,
            default=default_value,
            label=param_dict["title"],
            help=param_dict["description"],
            options=options,
            optional=is_nullable
        )
    
    # check for better solution
    def normalize_tool_name(self, tool_name: Union[str, None]):
        if tool_name is None:
            return None
        # Replace non-alphanumeric characters with underscores
        cleaned_name = tool_name.replace(" ", "_")
        # Convert to lowercase
        return cleaned_name
    
    def create_default_value(self, default_value):
        if default_value:
            default ="true"
        else:
            default = "false"
        return default

    def create_integer_param(self, param_name: str, param_dict: Dict, is_nullable: bool):
        """
        Create an integer parameter.

        Args:
            param_name (str): The name of the parameter.
            param_dict (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.

        Returns:
            IntegerParam: The created integer parameter.
        """
        default_value = param_dict["schema"].get("default")
        return self.gxtp.IntegerParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            value=default_value,
            optional=is_nullable
        )

    def create_float_param(self, param_name: str, param_dict: Dict, is_nullable: bool):
        """
        Create a float parameter.

        Args:
            param_name (str): The name of the parameter.
            param_dict (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.

        Returns:
            FloatParam: The created float parameter.
        """
        default_value = param_dict["schema"].get("default")
        return self.gxtp.FloatParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            value=default_value,
            optional=is_nullable
        )

    def create_data_param(self, param_name: str, param_dict: Dict, param_extended_schema: Dict, is_nullable, isArray: bool):
        # change for return for not array
        enum_values = []
        isArrayName = "isArray" + param_name
        if isArray:
            self.extract_enum(param_extended_schema['items'], enum_values)
            self.executable_dict[isArrayName] = True
        else:
            self.extract_enum(param_extended_schema, enum_values)
            self.executable_dict[isArrayName] = False

        data_types = ', '.join({value.split('/')[-1] for value in enum_values})
        return self.gxtp.DataParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"] + "The following data types are allowed in the txt file: " + data_types,
            format="txt",
            optional=is_nullable
        )

    def create_select_param_output(self, param_name: str, param_dict: Dict, param_extended_schema: Dict):
        enum_values = []
        self.extract_enum(param_extended_schema, enum_values)
        data_types_dict = {data_type: data_type.split('/')[-1] for data_type in enum_values}
        #pprint(data_types_dict)
        return self.gxtp.SelectParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            options=data_types_dict
        )
    
    def extract_enum(self, schema_item: Dict, enum_values: List):
        """
        Recursively extracts enum values from a JSON schema item.

        Args:
            schema_item (dict): The JSON schema item to extract enum values from.
            enum_values (list): A list to store the extracted enum values.

        Returns:
            None
        """
        lst = []
        if 'enum' in schema_item:
            enum_values.extend(schema_item['enum'])
            lst.extend(schema_item['enum'])
        elif 'properties' in schema_item:
            for prop in schema_item['properties'].values():
                self.extract_enum(prop, enum_values)
        elif 'oneOf' in schema_item:
            for option in schema_item['oneOf']:
                self.extract_enum(option, enum_values)
        elif 'allOf' in schema_item:
            for sub_item in schema_item['allOf']:
                self.extract_enum(sub_item, enum_values)
        
        #pprint(lst)

    def create_params(self, input_schema: Dict, output_schema: Dict, transmission_schema: Dict):
        """
        Create parameters based on input, output, and transmission schemas. Everything will be in the input tab of the Galaxy XML.

        Example of XML representation:
        <inputs>
            <param name="input_param" type="data" />
            <param name="output_param" type="data" />
        </inputs>

        Args:
            input_schema (Dict): The JSON schema for input parameters.
            output_schema (Dict): The JSON schema for output parameters.
            transmission_schema (Dict): The JSON schema for output transmission.

        Returns:
            List: A list of created parameters.
        """
        inputs = self.gxtp.Inputs()
        for param_name, param_dict in input_schema.items():
            param_schema = param_dict.get("schema")
            param_extended_schema = param_dict.get("extended-schema")
            param_type = param_schema.get("type")

            is_nullable = param_schema.get("nullable", False)
            if param_type == "string":
                if param_schema.get("enum"):
                    param = self.create_select_param(param_name, param_dict, is_nullable, param_type_bool=False)
                else:
                    param = self.create_text_param(param_name, param_dict, is_nullable)
            elif param_type == "integer":
                param = self.create_integer_param(param_name, param_dict, is_nullable)
            elif param_type == "number":
                param = self.create_float_param(param_name, param_dict, is_nullable)
            elif param_type == "boolean":
                param = self.create_select_param(param_name, param_dict, is_nullable, param_type_bool=True)
            elif param_extended_schema is not None:
                is_array = param_extended_schema.get("type") == "array"
                param = self.create_data_param(
                    param_name=param_name,
                    param_dict=param_dict,
                    param_extended_schema=param_extended_schema,
                    is_nullable=is_nullable,
                    isArray=is_array
                )

            else:
                # Handle unsupported parameter types gracefully
                print(f"Warning: Parameter '{param_name}' with unsupported type '{param_type}'")
                continue
            inputs.append(param)
        self.create_select_raw_param(inputs)
        self.create_output_param(output_schema=output_schema, inputs=inputs, transmission_schema=transmission_schema)

        return inputs

    def create_select_raw_param(self, inputs):
        """
        Create a select parameter for choosing between "raw" and "document" options.

        This method creates a select parameter for choosing between "raw" and "document"
        options, adds it to the provided list of inputs, and returns the modified list.

        Parameters:
        - inputs (list):False A list of input parameters.

        Returns:
        - list: The list of input parameters with the new select parameter added.
        """
        # Define dictionary of options and set default value
        dictionary_options = {"raw": "raw", "document": "document"}
        default_value = "document"

        # Set help description and label (if necessary)
        help_description = "Choose 'raw' for raw data or 'document' for document data."
        label = "Response Type"  # Label can be adjusted based on requirements

        # Create select parameter
        param = self.gxtp.SelectParam(
            name="response",
            default=default_value,
            options=dictionary_options,
            label=label,
            help=help_description
        )

        # Add parameter to the list of inputs
        inputs.append(param)

        return inputs

    def choose_transmission_mode(self, section: List, name: str, available_transmissions: Dict):
        """
        Adds a parameter to select transmission mode to a given section.

        Args:
            section (list): The section to which the parameter will be appended.
            item_number (int): The number of the item.
            available_transmissions (list): List of available transmission modes.

        Returns:
            list: The updated section with the added parameter.
        """
        label = "Choose the transmission mode"
        # Create a dictionary of transmission options
        transmission_options = {transmission: transmission for transmission in available_transmissions}

        default_transmission = "reference"
        param_name = "transmissionMode_" + str(name)

        # Create the parameter object
        param = self.gxtp.SelectParam(name=param_name, default=default_transmission, options=transmission_options, label=label)

        # Append the parameter to the section
        section.append(param)

        return section

    def create_output_param(self, output_schema: Dict, inputs: List, transmission_schema: Dict):
        """
        Create output parameters based on provided output schema and transmission schema.

        Args:
            output_schema (Dict): JSON schema containing output parameters.
            inputs (List): List of input parameters to which output parameters will be appended.
            All inputs parameters will be in Inputs of the galaxy xml
            transmission_schema (Dict): JSON schema containing output transmission information.

        Returns:
            None
        """
        # output_section = self.gxtp.Section(name="Output",
        # title="Choose the output format and/or transmission mode", expanded=True)

        for item_number, (param_name, param_dict) in enumerate(output_schema.items(), start=1):
            param_schema = param_dict.get("schema")
            param_extended_schema = param_dict.get("extended-schema")
            param_type = param_schema.get("type")
            output_param_name = f"outputType{item_number}_{param_name}"
            enum_values = []
            if param_type == "string":
                if param_schema.get("enum"):
                    param = self.create_select_param(output_param_name, param_dict, is_nullable=False)
                    enum_values = param_schema.get("enum")
                else:
                    # check for correct value for is_nullable
                    param = self.create_text_param(output_param_name, param_dict, is_nullable=False)
            elif param_extended_schema is not None:
                param = self.create_select_param_output(output_param_name, param_dict, param_extended_schema)
                self.extract_enum(param_extended_schema, enum_values=enum_values)
            elif param_type == "number":
                # param = self.create_float_param(output_param_name, param_dict, is_nullable=False)
                param = None
            else:
                # Handle unsupported parameter types gracefully
                print(f"Warning: Parameter '{output_param_name}' with unsupported type '{param_type}'")
                continue
            
            self.output_type_list[output_param_name] = enum_values

            output_param_section_name = f"OutputSection_{param_name}"
            output_param_section = self.gxtp.Section(
                name=output_param_section_name,
                title="Select the appropriate transmission mode for the output format and the output value",
                expanded=True
            )
            if param is not None:
                output_param_section.append(param)
            self.choose_transmission_mode(
                output_param_section,
                name=param_name,
                available_transmissions=transmission_schema
            )
            # output_section.append(output_param_section)
            inputs.append(output_param_section)
        #pprint(self.output_type_list)

    def define_command(self, title):
        """
        Define a command line of Galaxy Xml
        Always add name and title to command line. Additional commands are add with the exectutable dict, command line is a string

        Args:
            title (str): The title of the command.

        Returns:
            str: The formatted command.
        """
        self.executable_dict["name"] = title
        print(self.executable_dict)
        return self.executable + self.dict_to_string(self.executable_dict)

    def dict_to_string(self, dictionary: Dict):
        """
        Convert a dictionary to a string.

        Args:
            dictionary (dict): The dictionary to be converted.

        Returns:
            str: The string representation of the dictionary.
        """
        return ' '.join([f" {key} {value}" for key, value in dictionary.items()])


    # do to check with None
    def define_output_options(self):
        outputs = self.gxtp.Outputs()
        pprint(self.output_type_list)
        for key, values in self.output_type_list.items():
            print(values)
            if len(values) > 0:
                form = values[0].split('/')[-1]
                name = "output_data"
                param = self.gxtp.OutputData(name=name, format=form)
                self.executable_dict[name] = "$"+name
                change = self.gxtp.ChangeFormat()
                change_response = self.gxtp.ChangeFormatWhen(input="response", value="document", format="txt")
                change.append(change_response)
                for i in range(1,len(values)):
                    form = values[i].split('/')[-1]
                    change_i = self.gxtp.ChangeFormatWhen(input=key, value=values[i], format=form)
                    change.append(change_i)
                    param.append(change)
                outputs.append(param)

        return outputs

    def define_requirements(self):
        requirements = self.gxtp.Requirements()
        requirements.append(self.gxtp.Requirement(type="package", version="3.9", value="python"))
        return requirements

    def define_tests(self):
        tests = self.gxtp.Tests()
        test_a = self.gxtp.Test()
        param = self.gxtp.TestParam(name="response", value="document")
        output = self.gxtp.TestOutput(name="output_data", value="txt")
        test_a.append(output)
        test_a.append(param)

        tests.append(test_a)
        return tests

    def create_citations(self):
        citations = self.gxtp.Citations()
        citations.append(self.gxtp.Citation(type="bibtex", value="Josh"))
        return citations
