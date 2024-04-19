
from galaxyxml import tool
import galaxyxml.tool.parameters as gtpx

from pprint import pprint

class Galaxyxmltool:
    def __init__(self, name, id, version, description) -> None:
        self.gxt = tool.Tool(name=name, id = id, version=version, description=description, executable="$__tool_directory__/openapi.py")
        self.gxtp = gtpx

    def get_tool(self):
        return self.gxt
        

    def create_text_param(self, param_name, param_dict):
        return self.gxtp.TextParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            optional=False,
        )

    def create_select_param(self,param_name, param_dict):
        if param_dict["schema"].get("enum") is not None:
            data_types = param_dict["schema"]["enum"]
            data_types_dict = {data_type: data_type for data_type in data_types}
        else:
            print("To Do implement it")
        return self.gxtp.SelectParam(
            name=param_name,
            default=param_dict["schema"].get("default"),
            label=param_dict["title"],
            help=param_dict["description"],
            options=data_types_dict,
        )

    def create_integer_param(self, param_name, param_dict):
        default_value = param_dict["schema"].get("default", 0)
        return self.gxtp.IntegerParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            value=default_value
        )

    def create_float_param(self,param_name, param_dict):
        default_value = param_dict["schema"].get("default", 0)
        print(default_value)
        return self.gxtp.FloatParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            value=default_value
        )

    def create_boolean_param(self, param_name, param_dict):
        default_value = param_dict["schema"].get("default", False)
        return self.gxtp.BooleanParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            checked=default_value
        )

    def create_data_param(self, param_name, param_dict, param_extended_schema, isArray: bool):
        enum_values = []
        if isArray:
            self.extract_enum(param_extended_schema['items'], enum_values)
        else:
            self.extract_enum(param_extended_schema, enum_values)
        
        unique_enum_values = ','.join({value.split('/')[-1] for value in enum_values})
        return self.gxtp.DataParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            format="txt"
        )


    def create_select_param_output(self, param_name, param_dict, param_extended_schema):
        enum_values = []
        self.extract_enum(param_extended_schema, enum_values)
        unique_enum_values = list({value.split('/')[-1] for value in enum_values})
        data_types_dict = {data_type: data_type for data_type in unique_enum_values}
        return self.gxtp.SelectParam(
            name=param_name,
            label=param_dict["title"],
            help=param_dict["description"],
            options=data_types_dict
        )

    def extract_enum(self, schema_item, enum_values):
        if 'enum' in schema_item:
            enum_values.extend(schema_item['enum'])
        elif 'properties' in schema_item:
            for prop in schema_item['properties'].values():
                self.extract_enum(prop, enum_values)
        elif 'oneOf' in schema_item:
            for option in schema_item['oneOf']:
                self.extract_enum(option, enum_values)
        elif 'allOf' in schema_item:
            for sub_item in schema_item['allOf']:
                self.extract_enum(sub_item, enum_values)

    def create_params(self, inputs_json, outputs_json, output_transmission_json):
        inputs = self.gxtp.Inputs()
        pprint(inputs_json)
        for param_name, param_dict in inputs_json.items():
            param_schema = param_dict.get("schema")
            param_extended_schema = param_dict.get("extended-schema")
            param_type = param_schema.get("type")
            
            if param_type == "string":
                if param_schema.get("enum"):
                    param = self.create_select_param(param_name, param_dict)
                else:
                    param = self.create_text_param(param_name, param_dict)
            elif param_type == "integer":
                param = self.create_integer_param(param_name, param_dict)
            elif param_type == "number":
                param = self.create_float_param(param_name, param_dict)
            elif param_type == "boolean":
                param = self.create_boolean_param(param_name, param_dict)
            elif param_extended_schema is not None:
                is_array = param_extended_schema.get("type") == "array"
                param = self.create_data_param(param_name, param_dict, param_extended_schema, is_array)
            else:
                # Handle unsupported parameter types gracefully
                print(f"Warning: Parameter '{param_name}' with unsupported type '{param_type}'")
                continue
            
            inputs.append(param)
        self.create_select_raw_param(inputs)
        self.create_output_param(output_json=outputs_json, inputs=inputs,output_transmission_json=output_transmission_json)

        return inputs
    
    def create_select_raw_param(self, inputs):
        """
        Create a select parameter for choosing between "raw" and "document" options.

        This method creates a select parameter for choosing between "raw" and "document"
        options, adds it to the provided list of inputs, and returns the modified list.

        Parameters:
        - inputs (list): A list of input parameters.

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
        param = self.gxtp.SelectParam(name="response", default=default_value, options=dictionary_options, label=label, help=help_description)

        # Add parameter to the list of inputs
        inputs.append(param)

        return inputs
    
    def choose_transmission_mode(self, section, item_number, available_transmissions):
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
        #pprint(available_transmissions)
        
        # Create a dictionary of transmission options
        transmission_options = {transmission: transmission for transmission in available_transmissions}
        
        default_transmission = "reference"
        param_name = "transmissionMode_" + str(item_number)
        
        # Create the parameter object
        param = self.gxtp.SelectParam(name=param_name, default=default_transmission, options=transmission_options, label=label)
        
        # Append the parameter to the section
        section.append(param)
        
        return section

    def create_output_param(self, output_json, inputs, output_transmission_json):
        """
        Create output parameters based on provided JSON.

        Args:
            output_json (dict): JSON containing output parameters.
            inputs (list): List to which parameters will be appended.
            output_transmission_json (dict): JSON containing output transmission information.

        Returns:
            None
        """
        #output_section = self.gxtp.Section(name="Output", title="Choose the output format and/or transmission mode", expanded=True)

        for item_number, (param_name, param_dict) in enumerate(output_json.items(), start=1):
            param_schema = param_dict.get("schema")
            param_extended_schema = param_dict.get("extended-schema")
            param_type = param_schema.get("type")
            output_param_name = f"outputType{item_number}_{param_name}"

            if param_type == "string":
                if param_schema.get("enum"):
                    param = self.create_select_param(output_param_name, param_dict)
                else:
                    param = self.create_text_param(output_param_name, param_dict)
            elif param_extended_schema is not None:
                param = self.create_select_param_output(output_param_name, param_dict, param_extended_schema)
            elif param_type == "number":
                param = self.create_float_param(output_param_name, param_dict)
            else:
                # Handle unsupported parameter types gracefully
                print(f"Warning: Parameter '{output_param_name}' with unsupported type '{param_type}'")
                continue

            output_param_section_name = f"OutputSection_{item_number}"
            output_param_section = self.gxtp.Section(name=output_param_section_name, title="Select the appropriate transmission mode for the output format", expanded=True)
            output_param_section.append(param)
            self.choose_transmission_mode(output_param_section, item_number=item_number, available_transmissions=output_transmission_json)
            #output_section.append(output_param_section)

            inputs.append(output_param_section)

            
    
    def define_output_options(self):
        outputs = self.gxtp.Outputs()
        param = self.gxtp.OutputData(name="output_data", format="png")
        
        change = self.gxtp.ChangeFormat()
        change_a = self.gxtp.ChangeFormatWhen(input="outputType1_out", value="tiff", format="tiff")
        change_b = self.gxtp.ChangeFormatWhen(input="outputType1_out", value="jepg", format="jepg")
        #change_a = self.gxtp.ChangeFormatWhen(input="OutputSection_1", value="tiff", format="tiff")
        #change_b = self.gxtp.ChangeFormatWhen(input="OutputSection_1", value="jepg", format="jepg")
        change.append(change_a)
        change.append(change_b)
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
        param = self.gxtp.TestParam(name="outputType1_out", value="png")
        output = self.gxtp.TestOutput(name="output_data", value="png")
        test_a.append(output)
        test_a.append(param)

        tests.append(test_a)
        return tests
    
    def create_citations(self):
        citations = self.gxtp.Citations()
        citations.append(self.gxtp.Citation(type="bibtex", value = "Josh"))
        return citations
