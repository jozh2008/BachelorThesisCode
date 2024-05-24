from galaxyxml import tool
import galaxyxml.tool.parameters as gtpx

from pprint import pprint
from typing import Dict, List, Union
import re
import copy
import math


class Galaxyxmltool:
    def __init__(self, name, id, version, description) -> None:
        self.executable = "$__tool_directory__/Code/openapi.py"
        self.gxt = tool.Tool(
            name=name, id=id, version=version, description=description, executable=""
        )
        self.gxtp = gtpx
        self.executable_dict = {}
        self.output_type_dictionary = {}
        self.output_type = "outputType"
        self.output_name_list = []
        self.output_data = "output_data"

    def get_tool(self):
        return self.gxt

    def create_text_param(
        self,
        param_name: str,
        param_schema: Union[Dict, None],
        is_nullable: bool,
        title: Union[str, None],
        description: Union[str, None],
    ):
        """
        Create a text parameter for the Galaxy interface.

        Args:
            param_name (str): The name of the parameter.
            param_schema (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.

        Returns:
            TextParam: The created text parameter.
        """
        if param_schema is not None:
            default_value = param_schema.get("default")
        param = self.gxtp.TextParam(
            name=param_name,
            label=title,
            help=description,
            value=default_value,
            optional=is_nullable,
        )
        if not is_nullable:
            param.append(self.gxtp.ValidatorParam(name="validator", type="empty_field"))
        return param

    def create_select_param(
        self,
        param_name: str,
        param_schema: Dict,
        is_nullable: bool,
        param_type_bool: bool,
        title: str,
        description: str,
    ):
        """
        Create a select parameter for the Galaxy interface.

        Args:
            param_name (str): The name of the parameter.
            param_schema (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.
            param_type_bool (bool): Indicates whether the parameter is a boolean.

        Returns:
            SelectParam: The created select parameter.
        """
        enum_values = param_schema.get("enum")
        if enum_values is not None:
            # Merge enum values if they are split for better readability
            enum_values = self.merge_strings(enum_values=enum_values)
            options = {self.normalize_name(value): value for value in enum_values}
        elif param_type_bool:
            options = {"true": "true", "false": "false"}
        else:
            # If enum values are not provided, handle this case gracefully
            pprint(
                "Warning: Enum values are not provided for select parameter. Implementation needed."
            )
            options = {}  # Placeholder for options

        default_value = param_schema.get("default")
        # pprint(default_value)

        if default_value is not None and param_type_bool:
            default_value = self.create_default_value(default_value=default_value)

        # Normalize default values, ensuring they are keys in the options dictionary
        default_value = self.normalize_name(name=default_value)
        return self.gxtp.SelectParam(
            name=param_name,
            default=default_value,
            label=title,
            help=description,
            options=options,
            optional=is_nullable,
        )

    def create_number_param(
        self,
        param_name: str,
        is_nullable: bool,
        title: Union[str, None],
        description: Union[str, None],
        default_value: Union[float, int, None],
        param_type: str,
    ):
        param_class = getattr(self.gxtp, param_type)
        param = self.gxtp.Conditional(
            name="cond",
            label=f"Do you want to add optional parameter {param_name}",
        )
        options = {"yes": "yes", "no": "no"}
        default_select = "yes" if default_value is not None else "no"
        param.append(
            self.gxtp.SelectParam(
                name=f"select{param_name}",
                label=f"Do you want to add optional parameter {param_name}",
                help=description,
                options=options,
                default=default_select,
            )
        )
        when_a = self.gxtp.When(value="yes")
        when_a.append(
            param_class(
                name=param_name,
                label=title,
                help=description,
                value=default_value,
                optional=is_nullable,
            )
        )
        param.append(when_a)
        when_b = self.gxtp.When(value="no")
        param.append(when_b)

        return param

    def create_integer_param(
        self,
        param_name: str,
        param_schema: Union[Dict, None],
        is_nullable: bool,
        title: Union[str, None],
        description: Union[str, None],
    ):
        """
        Create an integer parameter.

        Args:
            param_name (str): The name of the parameter.
            param_dict (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.

        Returns:
            IntegerParam: The created integer parameter.
        """
        param_type = "IntegerParam"
        default_value = param_schema.get("default") if param_schema else None
        if is_nullable:
            return self.create_number_param(
                param_name=param_name,
                is_nullable=is_nullable,
                title=title,
                description=description,
                default_value=default_value,
                param_type=param_type,
            )

        return self.gxtp.IntegerParam(
            name=param_name, label=title, help=description, value=default_value
        )

    def create_float_param(
        self,
        param_name: str,
        param_schema: Union[Dict, None],
        is_nullable: bool,
        title: Union[str, None],
        description: Union[str, None],
    ):
        """
        Create a float parameter.

        Args:
            param_name (str): The name of the parameter.
            param_dict (Dict): The dictionary containing parameter details.
            is_nullable (bool): Indicates whether the parameter can be null.

        Returns:
            FloatParam: The created float parameter.
        """
        param_type = "FloatParam"
        default_value = param_schema.get("default") if param_schema else None
        if is_nullable:
            return self.create_number_param(
                param_name=param_name,
                is_nullable=is_nullable,
                title=title,
                description=description,
                default_value=default_value,
                param_type=param_type,
            )

        return self.gxtp.FloatParam(
            name=param_name, label=title, help=description, value=default_value
        )

    def create_data_param(
        self,
        param_name: str,
        param_extended_schema: Dict,
        is_nullable: bool,
        isArray: bool,
        title: str,
        description: str,
    ):
        # change for return for not array
        enum_values = []
        isArrayName = "isArray" + param_name
        if isArray:
            self.extract_enum(param_extended_schema["items"], enum_values)
            self.executable_dict[isArrayName] = True
        else:
            self.extract_enum(param_extended_schema, enum_values)
            self.executable_dict[isArrayName] = False

        data_types = ", ".join({value.split("/")[-1] for value in enum_values})
        return self.gxtp.DataParam(
            name=param_name,
            label=title,
            help=f"{description} The following data types are allowed in the txt file:  {data_types}",
            format="txt",
            optional=is_nullable,
        )

    # To do:
    def create_object_param(
        self,
        param_name: str,
        param_schema: Dict,
        is_nullable: bool,
        title: str,
        description: str,
    ):
        required = param_schema.get("required", [])
        enum_values = []
        section = self.create_section(
            name=param_name, title=title, description=description
        )
        for req in required:
            schema = param_schema["properties"][req]
            schema_type = schema.get("type")
            if schema_type == "string":
                enum_values = schema.get("enum")
                options = {value: value for value in enum_values}
                param = self.gxtp.SelectParam(
                    name=req, optional=is_nullable, options=options
                )
            elif schema_type == "array":
                # To do: Check best param for array with min and max Items
                array_items = schema.get("items")
                min_items, max_items = self.get_array_length(schema)
                array_type = array_items.get("type")
                param = self.create_array_param(req, array_type, min_items, max_items)

            section.append(param)

        return section

    def get_array_length(self, schema: Dict):
        """
        Get array length
        """
        array_length = schema.get("oneOf")
        min_items = math.inf
        max_items = -math.inf

        for dictionary in array_length:
            max_items = max(max_items, dictionary.get("maxItems", -math.inf))
            min_items = min(min_items, dictionary.get("minItems", math.inf))

        return min_items, max_items

    def create_array_param(
        self, name: str, array_type: str, min_items: int, max_items: int
    ):
        param = self.gxtp.Repeat(
            name=name, title="Array item", min=min_items, max=max_items
        )

        if array_type == "number":
            data = self.create_float_param(
                param_name="floatData",
                param_schema=None,
                is_nullable=False,
                title=None,
                description=None,
            )
        elif array_type == "integer":
            data = self.create_integer_param(
                param_name="integerData",
                param_schema=None,
                is_nullable=False,
                title=None,
                description=None,
            )
        elif array_type == "string":
            data = self.create_text_param(
                param_name="textData",
                param_schema=None,
                is_nullable=False,
                title=None,
                description=None,
            )
        else:
            print("Array type not supported yet")
            data = None

        param.append(data)
        return param

    def create_section(self, name: str, title: str, description=None):
        return self.gxtp.Section(
            name=name, title=title, help=description, expanded=True
        )

    def create_params(
        self, input_schema: Dict, output_schema: Dict, transmission_schema: Dict
    ):
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
            param_name = self.replace_dot(param_name)
            param_schema = param_dict.get("schema")
            param_extended_schema = param_dict.get("extended-schema")
            param_type = param_schema.get("type")
            is_nullable = param_schema.get("nullable", False)
            description = param_dict.get("description")
            title = param_dict.get("title")

            if param_type == "string":
                if param_schema.get("enum"):
                    param = self.create_select_param(
                        param_name=param_name,
                        param_schema=param_schema,
                        is_nullable=is_nullable,
                        param_type_bool=False,
                        title=title,
                        description=description,
                    )
                else:
                    param = self.create_text_param(
                        param_name=param_name,
                        param_schema=param_schema,
                        is_nullable=is_nullable,
                        title=title,
                        description=description,
                    )
            elif param_type == "integer":
                param = self.create_integer_param(
                    param_name=param_name,
                    param_schema=param_schema,
                    is_nullable=is_nullable,
                    title=title,
                    description=description,
                )
            elif param_type == "number":
                param = self.create_float_param(
                    param_name=param_name,
                    param_schema=param_schema,
                    is_nullable=is_nullable,
                    title=title,
                    description=description,
                )
            elif param_type == "boolean":
                param = self.create_select_param(
                    param_name=param_name,
                    param_schema=param_schema,
                    is_nullable=is_nullable,
                    param_type_bool=True,
                    title=title,
                    description=description,
                )
            elif param_extended_schema is not None:
                is_array = param_extended_schema.get("type") == "array"
                param = self.create_data_param(
                    param_name=param_name,
                    param_extended_schema=param_extended_schema,
                    is_nullable=is_nullable,
                    isArray=is_array,
                    title=title,
                    description=description,
                )
            elif param_type == "object":
                param = self.create_object_param(
                    param_name=param_name,
                    param_schema=param_schema,
                    is_nullable=is_nullable,
                    title=title,
                    description=description,
                )

            else:
                # Handle unsupported parameter types gracefully
                print(
                    f"Warning: Parameter '{param_name}' with unsupported type '{param_type}'"
                )
                continue
            inputs.append(param)
        self.choose_prefer(inputs=inputs)
        self.create_select_raw_param(inputs=inputs)
        self.create_output_param(
            output_schema=output_schema,
            inputs=inputs,
            transmission_schema=transmission_schema,
        )

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
            help=help_description,
        )

        # Add parameter to the list of inputs
        inputs.append(param)

        return inputs

    def choose_prefer(self, inputs):
        """
        Creates a select parameter to choose between "return=representation", "return=minimal",
        and "respond-async;return=representation". The specification is for synchronous or
        asynchronous executions, with asynchronous execution as the default value.
        """

        label = "Choose the Prefer"
        prefer_options = {
            "return=representation": "return=representation",
            "return=minimal": "return=minimal",
            "respond-async;return=representation": "respond-async;return=representation",
        }

        default_value = "respond-async;return=representation"

        param = self.gxtp.SelectParam(
            name="prefer",
            default=default_value,
            options=prefer_options,
            label=label,
        )

        # Add parameter to the list of inputs
        inputs.append(param)

        return inputs

    def choose_transmission_mode(
        self, section: List, name: str, available_transmissions: Dict
    ):
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
        transmission_options = {
            transmission: transmission for transmission in available_transmissions
        }

        default_transmission = "reference"
        param_name = "transmissionMode_" + str(name)

        # Create the parameter object
        param = self.gxtp.SelectParam(
            name=param_name,
            default=default_transmission,
            options=transmission_options,
            label=label,
        )

        # Append the parameter to the section
        section.append(param)

        return section

    # To do: Implement solution for param_type object
    def create_output_param(
        self, output_schema: Dict, inputs: List, transmission_schema: Dict
    ):
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

        for param_name, param_dict in output_schema.items():
            param_name = self.replace_dot(param_name)
            param_schema = param_dict.get("schema")
            param_extended_schema = param_dict.get("extended-schema")
            param_type = param_schema.get("type")
            output_param_name = f"{self.output_type}_{param_name}"
            title = param_schema.get("title")
            description = param_schema.get("description")
            enum_values = []

            param, enum_values = self.process_output_param(
                output_param_name=output_param_name,
                param_extended_schema=param_extended_schema,
                param_schema=param_schema,
                param_type=param_type,
                enum_values=enum_values,
                title=title,
                description=description,
            )
            self.output_type_dictionary[output_param_name] = enum_values
            self.output_name_list.append(param_name)  # just name of output

            output_param_section_name = f"OutputSection_{param_name}"
            title = "Select the appropriate transmission mode for the output format"
            output_param_section = self.create_section(
                name=output_param_section_name, title=title
            )
            if param is not None:
                output_param_section.append(param)
            self.choose_transmission_mode(
                output_param_section,
                name=param_name,
                available_transmissions=transmission_schema,
            )
            inputs.append(output_param_section)

    def process_output_param(
        self,
        output_param_name: str,
        param_extended_schema: Dict,
        param_schema: Dict,
        param_type: str,
        enum_values: List,
        title: str,
        description: str,
    ):
        # To Do: check string
        if param_type == "string":
            if param_schema.get("enum"):
                param = self.create_select_param(
                    param_name=output_param_name,
                    param_schema=param_schema,
                    is_nullable=False,
                    param_type_bool=False,
                    title=title,
                    description=description,
                )
                enum_values = param_schema.get("enum")

            else:
                # If no enum, then nothing to specify and so param is None
                param = None
        elif param_extended_schema is not None:
            param = self.create_select_param_output(
                output_param_name, param_extended_schema, title, description
            )
            self.extract_enum(param_extended_schema, enum_values=enum_values)
        elif param_type in ["number", "integer", "boolean", "object"]:
            # if not a string then param is None
            param = None
        else:
            # Handle unsupported parameter types gracefully
            print(
                f"Warning: Parameter '{output_param_name}' with unsupported type '{param_type}'"
            )
            param = None

        return param, enum_values

    # To do: Add docstring
    def create_select_param_output(
        self, param_name: str, param_extended_schema: Dict, title: str, description: str
    ):
        enum_values = []
        self.extract_enum(param_extended_schema, enum_values)
        data_types_dict = {
            data_type: data_type.split("/")[-1] for data_type in enum_values
        }
        return self.gxtp.SelectParam(
            name=param_name, label=title, help=description, options=data_types_dict
        )

    # To do: check for better solution
    def normalize_name(self, name: Union[str, None]):
        """
        Normalize a tool name by replacing spaces with underscores.

        This method is designed to prevent the splitting of strings with spaces
        in different commands within Galaxy XML.

        Args:
            tool_name (str or None): The name of the tool to normalize.

        Returns:
            str or None: The normalized tool name with spaces replaced by underscores,
                         or None if the input is None.
        """
        if name is None:
            return None

        # Replace spaces with underscores
        normalized_name = name.replace(" ", "_")

        return normalized_name

    def replace_dot(self, name):
        return name.replace(".", "_")

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
        if "enum" in schema_item:
            enum_values.extend(schema_item["enum"])
            lst.extend(schema_item["enum"])
        elif "properties" in schema_item:
            for prop in schema_item["properties"].values():
                self.extract_enum(prop, enum_values)
        elif "oneOf" in schema_item:
            for option in schema_item["oneOf"]:
                self.extract_enum(option, enum_values)
        elif "allOf" in schema_item:
            for sub_item in schema_item["allOf"]:
                self.extract_enum(sub_item, enum_values)

    def merge_strings(self, enum_values):
        """
        Merges adjacent string elements in the list if the current element (odd index i, starting from 0)
        begins with a space. The merged string is formed by combining it with the previous element (i-1).

        Args:
            enum_values (list): A list of string values.

        Returns:
            list: A new list containing merged strings.
        """
        merged_list = copy.deepcopy(enum_values)
        indices_not_to_merge = []
        merged_strings = []

        for i in range(1, len(enum_values)):
            current_string = enum_values[i]
            if current_string.startswith(" "):
                merged_list[i - 1] = f"{enum_values[i - 1]},{current_string}"
                indices_not_to_merge.append(i)

        for i in range(len(merged_list)):
            if i not in indices_not_to_merge:
                merged_strings.append(merged_list[i])

        return merged_strings

    def create_default_value(self, default_value):
        """
        Default value should be "true" and "false" instead of True and False.
        """
        if default_value:
            default = "true"
        else:
            default = "false"
        return default

    def dict_to_string(self, dictionary: Dict):
        """
        Convert a dictionary to a string.

        Args:
            dictionary (dict): The dictionary to be converted.

        Returns:
            str: The string representation of the dictionary.
        """
        return " ".join([f" {key} {value}" for key, value in dictionary.items()])

    def find_index(self, string, pattern):
        match = re.search(pattern=pattern, string=string)
        return match.end()

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
        return self.executable + self.dict_to_string(self.executable_dict)

    # possible output options need to be discussed, which is better
    def define_output_collections(self):
        outputs = self.gxtp.Outputs()
        name = self.output_data
        collection = self.gxtp.OutputCollection(name=name, type="list")
        discover = self.gxtp.DiscoverDatasets(pattern="__name_and_ext__")
        collection.append(discover)
        outputs.append(collection)
        return outputs

    # possible output options need to be discussed, which is better
    def define_output_options(self):
        """
        Define output options for each item in self.output_type_dictionray.

        This method creates output schemas for Galaxy XML based on the output types stored in the self.output_type_dictionary.

        If an output type has no corresponding value, it is skipped.
        If an output type has more than one entry, the format is changed to the corresponding chosen format.

        Returns:
            gxtp.Outputs: An instance of gxtp.Outputs containing the defined output options.
        """
        outputs = self.gxtp.Outputs()
        for key, values in self.output_type_dictionary.items():
            index = self.find_index(string=key, pattern=f"{self.output_type}_")
            name = f"{self.output_data}_{key[index:]}"
            self.executable_dict[name] = f"${name}"

            if not values:
                param = self.gxtp.OutputData(name=name, format="txt", label=name)
                outputs.append(param)
                continue

            form = values[0].split("/")[-1]
            param = self.gxtp.OutputData(name=name, format=form, label=name)

            change = self.gxtp.ChangeFormat()
            change_response = self.gxtp.ChangeFormatWhen(
                input="response", value="document", format="txt"
            )
            change.append(change_response)
            for value in values[1:]:
                form = value.split("/")[-1]
                change_i = self.gxtp.ChangeFormatWhen(
                    input=key, value=value, format=form
                )
                change.append(change_i)
                param.append(change)
            outputs.append(param)

        return outputs

    # To do add requirements
    def define_requirements(self):
        requirements = self.gxtp.Requirements()
        requirements.append(
            self.gxtp.Requirement(type="package", version="3.9", value="python")
        )
        return requirements

    # To do add tests
    def define_tests(self, api_dict, process):
        test_dictionary = self.get_test_dictionary(api_dict=api_dict, process=process)
        if test_dictionary is not None:
            example_list = self.get_test_examples(data=test_dictionary)
            return self.create_tests(examples=example_list)
        tests = self.gxtp.Tests()
        test_a = self.gxtp.Test()
        param = self.gxtp.TestParam(name="response", value="document")
        test_a.append(param)
        for output_name in self.output_name_list:
            name = f"{self.output_data}_{output_name}"
            output = self.gxtp.TestOutput(name=name, ftype="txt", value=f"{name}.txt")
            test_a.append(output)

        tests.append(test_a)
        return tests

    # To do refactor code after discussion
    def create_tests(self, examples):
        tests = self.gxtp.Tests()

        for ex in examples:
            test = self.gxtp.Test()
            inputs = ex.get("inputs", {})
            outputs = ex.get("outputs", {})
            response = ex.get("response", "")

            # Add response parameter
            test.append(self.gxtp.TestParam(name="response", value=response))

            # Process input parameters
            for key, value in inputs.items():
                if isinstance(value, list):
                    lst = [i.get("href") for i in value]
                    param = self.gxtp.TestParam(name=key, value=lst)
                elif isinstance(value, dict):
                    param = self.gxtp.TestParam(name=key, value=value.get("href"))
                else:
                    param = self.gxtp.TestParam(name=key, value=value)
                test.append(param)

            # Process output parameters
            for key, value in outputs.items():
                name = f"{self.output_data}_{key}"
                if response == "raw":
                    media_type = value["format"]["mediaType"].split("/")[-1]
                    param = self.gxtp.TestOutput(
                        name=name, ftype=media_type, value=f"{name}.{media_type}"
                    )
                else:
                    param = self.gxtp.TestOutput(
                        name=name, ftype="txt", value=f"{name}.txt"
                    )
                test.append(param)

            tests.append(test)

        return tests

    def get_test_examples(self, data):
        """
        Get all example values of the nested dictionary
        """
        examples = []

        post_data = data.get("post", {})
        request_body = post_data.get("requestBody", {})
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        examples_dict = json_content.get("examples", {})

        for example in examples_dict.values():
            examples.append(example.get("value"))

        return examples

    def get_test_dictionary(self, api_dict, process):
        """
        Extracts and returns the relevant part of the API request
        "https://ospd.geolabs.fr:8300/ogc-api/api",
        when the process has examples. This examples we want to use as test cases.
        """
        for pro in api_dict.keys():
            parts = pro.split("/")
            if len(parts) > 2 and process.__eq__(parts[2]):
                return api_dict[pro]
        return None

    # To do: What should I citate
    def create_citations(self):
        citations = self.gxtp.Citations()
        citations.append(self.gxtp.Citation(type="bibtex", value="Josh"))
        return citations
