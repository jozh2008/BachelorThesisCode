from galaxyxml import tool
import galaxyxml.tool.parameters as gtpx

from .macros_xml_generator import MacrosXMLGenerator

from typing import Dict, List
import re
import copy
import math


class GalaxyXmlTool:
    def __init__(self, name, id, version, description) -> None:
        self.executable = "$__tool_directory__/Code/create_api_json.py"
        self.macros_file_name = f"Macros/{name}_macros_.xml"
        self.gxt = tool.Tool(
            name=name,
            id=id,
            version="@TOOL_VERSION@+galaxy@VERSION_SUFFIX@",
            description=description,
            executable="",
            macros=[self.macros_file_name],
        )
        self.version = version
        self.version_suffix = "0"
        self.gxtp = gtpx
        self.executable_dict = {}
        self.output_type_dictionary = {}
        self.output_type = "outputType"
        self.output_name_list = []
        self.output_data = "output_data"

    def get_tool(self):
        """
        Retrieve the current tool instance from the Galaxy XML Tool (gxt) package.

        This method provides access to the current tool instance being managed
        by the `gxtp` attribute of the class. It is used to interface with the
        tool's configuration and parameters within the Galaxy environment.

        Returns:
            Tool: The current tool instance from the Galaxy XML Tool package.
        """
        return self.gxt

    def create_text_param(
        self,
        param_name: str,
        param_schema: Dict | None,
        is_nullable: bool,
        title: str | None,
        description: str | None,
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
        default_value = param_schema.get("default") if param_schema else None
        param = self.gxtp.TextParam(
            name=param_name,
            label=title,
            help=description,
            value=default_value,
            optional=is_nullable,
        )
        if not is_nullable:
            param.append(self.gxtp.ValidatorParam(name=None, type="empty_field"))
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
            # enum_values = self.merge_strings(enum_values=enum_values)
            options = {self.replace_space_with_underscore(value): value for value in enum_values}
        elif param_type_bool:
            options = {"true": "true", "false": "false"}
        else:
            # If enum values are not provided, handle this case gracefully
            print("Warning: Enum values are not provided for select parameter. Implementation needed.")
            options = {}  # Placeholder for options

        default_value = param_schema.get("default")

        if default_value is not None and param_type_bool:
            default_value = self.create_default_value(default_value=default_value)

        # Normalize default values, ensuring they are keys in the options dictionary
        default_value = self.replace_space_with_underscore(name=default_value)

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
        title: str | None,
        description: str | None,
        default_value: float | int | None,
        param_type: str,
    ):
        """
        Create a number parameter with conditional inclusion based on user choice.

        Args:
            param_name (str): The name of the parameter.
            is_nullable (bool): Indicates if the parameter is nullable.
            title (Union[str, None]): The title of the parameter.
            description (Union[str, None]): The description of the parameter.
            default_value (Union[float, int, None]): The default value for the parameter.
            param_type (str): The type of the parameter (e.g., 'FloatParam', 'IntegerParam').

        Returns:
            Conditional: The conditional parameter object.
        """

        # Create the conditional parameter to allow user to choose if they want to add the optional parameter
        param_class = getattr(self.gxtp, param_type)

        conditional_param = self.gxtp.Conditional(
            name=f"cond_{param_name}",
            label=f"Do you want to add optional parameter {param_name}?",
        )

        # Define options for the conditional selection
        options = {"yes": "yes", "no": "no"}
        default_select = "yes" if default_value is not None else "no"

        # Create and append the select parameter for the conditional choice
        select_param = self.gxtp.SelectParam(
            name=f"select_{param_name}",
            label=f"Do you want to add optional parameter {param_name}?",
            help=description,
            options=options,
            default=default_select,
        )

        # Create and append the parameter to be included when user selects 'yes'
        conditional_param.append(select_param)
        when_yes = self.gxtp.When(value="yes")
        number_param = param_class(
            name=param_name,
            label=title,
            help=description,
            value=default_value,
            optional=is_nullable,
        )

        when_yes.append(number_param)

        conditional_param.append(when_yes)

        # Create and append an empty 'when' block for 'no' option
        when_no = self.gxtp.When(value="no")
        conditional_param.append(when_no)

        return conditional_param

    def create_integer_param(
        self,
        param_name: str,
        param_schema: Dict | None,
        is_nullable: bool,
        title: str | None,
        description: str | None,
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

        return self.gxtp.IntegerParam(name=param_name, label=title, help=description, value=default_value)

    def create_float_param(
        self,
        param_name: str,
        param_schema: Dict | None,
        is_nullable: bool,
        title: str | None,
        description: str | None,
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

        return self.gxtp.FloatParam(name=param_name, label=title, help=description, value=default_value)

    def create_data_param(
        self,
        param_name: str,
        param_extended_schema: Dict,
        is_nullable: bool,
        is_array: bool,
        title: str,
        description: str,
    ):
        """
        Create a data parameter based on the provided schema and other properties.

        Args:
            param_name (str): The name of the parameter.
            param_extended_schema (Dict): The extended schema for the parameter.
            is_nullable (bool): Indicates if the parameter is nullable.
            is_array (bool): Indicates if the parameter is an array.
            title (str): The title of the parameter.
            description (str): The description of the parameter.

        Returns:
            DataParam: The created data parameter.
        """
        enum_values = []
        array_status_key = f"isArray{param_name}"
        # Extract enum values based on whether the parameter is an array
        if is_array:
            self.extract_enum(param_extended_schema.get("items", {}), enum_values)
            self.executable_dict[array_status_key] = True
        else:
            self.extract_enum(param_extended_schema, enum_values)
            self.executable_dict[array_status_key] = False

        # Generate a string of allowed data types from enum values
        data_types = ", ".join(value.split("/")[-1] for value in enum_values)

        # Create and return the data parameter
        return self.gxtp.DataParam(
            name=param_name,
            label=title,
            help=f"{description} The following data types are allowed in the txt file: {data_types}",
            format="txt",
            optional=is_nullable,
        )

    def create_object_param(
        self,
        param_name: str,
        param_schema: Dict,
        is_nullable: bool,
        title: str,
        description: str,
    ):
        """
        Create an object parameter with the specified schema, title, and description.

        Args:
            param_name (str): The name of the parameter.
            param_schema (Dict): The schema of the parameter which includes its properties and required fields.
            is_nullable (bool): Indicates if the parameter is nullable.
            title (str): The title of the parameter.
            description (str): The description of the parameter.

        Returns:
            section: The section containing the created parameters.
        """
        required_fields = param_schema.get("required", [])
        section = self.create_section(name=param_name, title=title, description=description)
        for field in required_fields:
            field_schema = param_schema["properties"][field]
            field_type = field_schema.get("type")
            if field_type == "string":
                param = self.create_select_param(
                    param_name=field,
                    param_schema=field_schema,
                    is_nullable=is_nullable,
                    param_type_bool=False,
                    title=field,
                    description="",
                )
            elif field_type == "array":
                array_items = field_schema.get("items")
                min_items, max_items = self.get_array_items(field_schema)
                array_type = array_items.get("type")
                param = self.create_array_param(
                    name=field,
                    item_type=array_type,
                    min_items=min_items,
                    max_items=max_items,
                    title=None,
                    description=None,
                    item_name=f"{array_type}Data",
                )
            section.append(param)

        return section

    def get_array_items(self, schema: Dict):
        """
        Get the minimum and maximum number of items allowed in an array based on the schema.

        Args:
            schema (Dict): The schema defining the array and its constraints.

        Returns:
            tuple: A tuple containing the minimum and maximum number of items allowed in the array.
        """
        constraints = schema.get("oneOf", [])
        min_items = math.inf
        max_items = -math.inf

        for constraint in constraints:
            max_items = max(max_items, constraint.get("maxItems", -math.inf))
            min_items = min(min_items, constraint.get("minItems", math.inf))

        return min_items, max_items

    def create_array_param(
        self,
        name: str,
        item_type: str,
        min_items: int,
        max_items: int,
        title: str | None,
        description: str | None,
        item_name: str,
    ):
        """
        Create an array parameter with specified constraints and item type.

        Args:
            name (str): The name of the parameter.
            array_type (str): The type of items in the array (e.g., 'number', 'integer', 'string').
            min_items (int): The minimum number of items in the array.
            max_items (int): The maximum number of items in the array.
            title (str): The title of the array parameter.
            description (str): The description of the array parameter.
            item_name (str): The name of the items within the array.

        Returns:
            param: The parameter object representing the array with the specified constraints.
        """
        param = self.gxtp.Repeat(name=name, title="Array item", min=min_items, max=max_items)

        if item_type == "number":
            data = self.create_float_param(
                param_name="floatData",
                param_schema=None,
                is_nullable=False,
                title=title,
                description=description,
            )
        elif item_type == "integer":
            data = self.create_integer_param(
                param_name="integerData",
                param_schema=None,
                is_nullable=False,
                title=title,
                description=description,
            )
        elif item_type == "string":
            data = self.create_text_param(
                param_name=item_name,
                param_schema=None,
                is_nullable=False,
                title=title,
                description=description,
            )
        else:
            raise ValueError(f"Array item type '{item_type}' is not supported")

        param.append(data)
        return param

    def create_section(self, name: str, title: str, description=None):
        """
        Create a section with the specified name, title, and optional description.

        Args:
            name (str): The name of the section.
            title (str): The title of the section.
            description (str, optional): The description of the section. Defaults to None.

        Returns:
            Section: The section object with the specified attributes.
        """
        return self.gxtp.Section(name=name, title=title, help=description, expanded=True)

    def create_params(self, input_schema: Dict, output_schema: Dict, transmission_schema: Dict):
        """
        Generate parameters based on the provided input, output, and transmission schemas.
        All parameters will be placed in the input tab of the Galaxy XML.

        Example of XML representation:
        <inputs>
            <param name="input_param" type="data" />
            <param name="output_param" type="data" />
        </inputs>

        Args:
        input_schema (Dict): JSON schema defining the input parameters.
        output_schema (Dict): JSON schema defining the output parameters.
        transmission_schema (Dict): JSON schema defining the transmission parameters.

        Returns:
        List: A list of generated parameters.
        """
        inputs = self.gxtp.Inputs()
        for param_name, param_info in input_schema.items():
            param_name = self.replace_dot_with_underscore(param_name)
            param_schema = param_info.get("schema")
            param_extended_schema = param_info.get("extended-schema")
            param_type = param_schema.get("type")
            is_nullable = param_schema.get("nullable", False)
            title = param_info.get("title")
            description = param_info.get("description")
            if title != description:
                description = f"{title} {description}"
            title = param_name

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
                is_nullable = param_extended_schema.get("nullable", False)
                param = self.create_data_param(
                    param_name=param_name,
                    param_extended_schema=param_extended_schema,
                    is_nullable=is_nullable,
                    is_array=is_array,
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
                print(f"Warning: Parameter '{param_name}' with unsupported type '{param_type}'")
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

        description = (
            "Choose 'raw' to get the raw data or 'document' for retrieving a URL. "
            "The URL can be used for workflows, while the raw data is the download of the URL"
        )

        # Set help description and label (if necessary)
        help_description = "Choose 'raw' for raw data or 'document' for document data."
        label = "Response Type"  # Label can be adjusted based on requirements
        section = self.create_section(
            name="Section_response",
            title="Choose the response type",
            description=description,
        )
        # Create select parameter
        param = self.gxtp.SelectParam(
            name="response",
            default=default_value,
            options=dictionary_options,
            label=label,
            help=help_description,
        )

        section.append(param)
        # Add parameter to the list of inputs
        inputs.append(section)

        return inputs

    def choose_prefer(self, inputs):
        """
        Creates a select parameter to choose between "return=representation", "return=minimal",
        and "respond-async;return=representation". The specification is for synchronous or
        asynchronous executions, with asynchronous execution as the default value.
        """

        label = "Prefer"
        async_execution = "respond-async;return=representation"
        minimal_execution = "return=minimal"
        sync_execution = "return=representation"
        prefer_options = {
            sync_execution: sync_execution,
            minimal_execution: minimal_execution,
            async_execution: async_execution,
        }

        default_value = sync_execution
        description = (
            "Choose between 'return=representation', 'return=minimal', and 'respond-async;return=representation'."
            "The specification is for synchronous or asynchronous executions, "
            "with synchronous execution as the default value"
        )
        section = self.create_section(name="Section_prefer", title="Choose the prefer", description=description)
        param = self.gxtp.SelectParam(
            name="prefer",
            default=default_value,
            options=prefer_options,
            label=label,
            help=None,
        )
        section.append(param)

        # Add parameter to the list of inputs
        inputs.append(section)

        return inputs

    def choose_transmission_mode(self, section: List, name: str, available_transmissions: List):
        """
        Adds a parameter to select transmission mode to a given section.

        Args:
            section (list): The section to which the parameter will be appended.
            available_transmissions (list): List of available transmission modes.
            name (str): Name of the output

        Returns:
            list: The updated section with the added parameter.
        """
        label = "Choose the transmission mode"
        # Create a dictionary of transmission options
        transmission_options = {transmission: transmission for transmission in available_transmissions}

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

    def create_output_param(self, output_schema: Dict, inputs: List, transmission_schema: List):
        """
        Create output parameters based on provided output schema and transmission schema.

        Args:
            output_schema (Dict): JSON schema containing output parameters.
            inputs (List): List of input parameters to which output parameters will be appended.
                        All input parameters will be in Inputs of the Galaxy XML.
            transmission_schema (List): JSON schema containing output transmission information.

        Returns:
            None
        """
        for param_name, param_info in output_schema.items():
            param_name = self.replace_dot_with_underscore(param_name)
            param_schema = param_info.get("schema")
            param_extended_schema = param_info.get("extended-schema")
            param_type = param_schema.get("type")
            output_param_name = f"{self.output_type}_{param_name}"
            title = param_info.get("title")
            description = param_info.get("description")
            if title != description:
                description = f"{title} {description}"

            title = param_name

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
            if param is None:
                title = f"Select the appropriate transmission mode for {param_name}"
            else:
                title = f"Select the appropriate transmission mode for {param_name} and specify an output format"
            output_param_section = self.create_section(name=output_param_section_name, title=title)

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
        """
        Process an output parameter based on its type and schema information.

        Args:
            output_param_name (str): The name of the output parameter.
            param_extended_schema (Dict): The extended schema for the parameter, if available.
            param_schema (Dict): The schema for the parameter.
            param_type (str): The type of the parameter (e.g., 'string', 'number').
            enum_values (List): A list to store enumeration values if applicable.
            title (str): The title of the parameter.
            description (str): The description of the parameter.

        Returns:
            Tuple[Optional[Param], List]: The processed parameter and its enumeration values.
        """

        param = None
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
                enum_values = param_schema.get("enum", [])

            else:
                # No enum values, so no specific parameter is created
                param = None
        elif param_extended_schema is not None:
            param = self.create_select_param_output(
                param_name=output_param_name,
                param_extended_schema=param_extended_schema,
                title=title,
                description=description,
            )
            self.extract_enum(param_extended_schema, enum_values=enum_values)
        elif param_type in ["number", "integer", "boolean", "object"]:
            # Currently unsupported types for output parameters, set to None
            param = None
        else:
            # Handle unsupported parameter types gracefully
            print(f"Warning: Parameter '{output_param_name}' with unsupported type '{param_type}'")
            param = None

        return param, enum_values

    def create_select_param_output(self, param_name: str, param_extended_schema: Dict, title: str, description: str):
        """
        Create a select parameter for the output based on the extended schema.

        Args:
            param_name (str): The name of the parameter.
            param_extended_schema (Dict): The extended schema containing enumeration values.
            title (str): The title of the parameter.
            description (str): The description of the parameter.

        Returns:
            SelectParam: The created select parameter.
        """
        # Extract enumeration values from the extended schema
        enum_values = []
        self.extract_enum(schema_item=param_extended_schema, enum_values=enum_values)
        # Create a dictionary for data types based on the enumeration values
        data_types_dict = {data_type: data_type.split("/")[-1] for data_type in enum_values}

        # Return the created select parameter
        return self.gxtp.SelectParam(name=param_name, label=title, help=description, options=data_types_dict)

    def replace_space_with_underscore(self, name: str | None):
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

    def replace_dot_with_underscore(self, name: str) -> str:
        """
        Replace all dots in the provided string with underscores.

        This method is useful for sanitizing parameter names that may contain dots,
        which are not always allowed or are problematic in certain contexts.

        Args:
            name (str): The string in which dots need to be replaced.

        Returns:
            str: The modified string with dots replaced by underscores.
        """
        return name.replace(".", "_")

    def extract_enum(self, schema_item: Dict, enum_values: List):
        """
        Recursively extracts enum values from a JSON schema item.

        Args:
            schema_item (dict): The JSON schema item to extract enum values from.
            enum_values (list): A list to store the extracted enum values .

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

        for i in range(1, len(enum_values)):
            current_string = enum_values[i]
            if current_string.startswith(" "):
                merged_list[i] = f"{merged_list[i - 1]},{current_string}"
        return self.remove_duplicate(merged_list)

    def remove_duplicate(self, original_list: List):
        """
        Remove duplicates from a list while preserving the original order.

        This function takes a list as input and returns a new list with duplicate elements removed,
        preserving the original order of elements.

        Args:
        - original_list (list): The input list containing elements, including duplicates.

        Returns:
        - list: A new list with duplicate elements removed, preserving the original order.
        """

        unique_list = []

        for item in original_list:
            # Add item to the unique_list if it's not already present
            if item not in unique_list:
                unique_list.append(item)

        return unique_list

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
        """
        Find the index of the end of the first occurrence of a pattern in a string.

        Args:
            string (str): The input string to search.
            pattern (str): The pattern to search for in the string.

        Returns:
            int: The index of the end of the first occurrence of the pattern,
                 or -1 if the pattern is not found.
        """
        match = re.search(pattern=pattern, string=string)
        if match:
            return match.end()
        else:
            return -1

    def define_command(self, title):
        """
        Define a command line of Galaxy Xml
        Always add name and title to command line. Additional commands are add with the exectutable dict,
        command line is a string

        Args:
            title (str): The title of the command.

        Returns:
            str: The formatted command.
        """
        self.executable_dict["name"] = title
        return self.executable + self.dict_to_string(self.executable_dict)

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
            label_name = key[index:]
            name = f"{self.output_data}_{label_name}"
            self.executable_dict[name] = f"${name}"

            if not values:
                param = self.gxtp.OutputData(name=name, format="txt")
                outputs.append(param)
                continue
            form = values[0].split("/")[-1]
            param = self.gxtp.OutputData(name=name, format=form)

            change = self.gxtp.ChangeFormat()
            change_response = self.gxtp.ChangeFormatWhen(input="response", value="document", format="txt")
            change.append(change_response)
            for value in values[1:]:
                form = value.split("/")[-1]
                change_i = self.gxtp.ChangeFormatWhen(input=key, value=value, format=form)
                change.append(change_i)
                param.append(change)
            outputs.append(param)

        return outputs

    # To do add requirements
    def define_requirements(self):
        """
        Add the requirments for generating the Galaxy XML file.
        """
        requirements = self.gxtp.Requirements()
        requirements.append(self.gxtp.Requirement(type="package", version="3.10.12", value="python"))
        requirements.append(self.gxtp.Requirement(type="package", version="2.31.0", value="requests"))
        return requirements

    def define_macro(self):
        """Generates the macro.xml"""
        generator = MacrosXMLGenerator()
        generator.add_token("@TOOL_VERSION@", self.version)
        # starts with 0
        generator.add_token("@VERSION_SUFFIX@", self.version_suffix)
        file_path = f"Tools/{self.macros_file_name}"
        generator.generate_xml(filename=file_path)

    # To do add tests
    def define_tests(self, api_dict: Dict, process: str):
        """
        Define the tests for the given API dictionary and process.

        This method initializes a test dictionary from the given API dictionary
        and process. If the test dictionary is valid, it creates test examples and
        uses them to create tests. If not, it creates a default test setup.

        Args:
            api_dict (Dict): The dictionary containing API information.
            process (str): The specific process to define tests for.

        Returns:
            Tests: A Tests object populated with the defined tests.
        """
        # Get the test dictionary using the given API dictionary and process
        test_dictionary = self.get_test_dictionary(api_dict=api_dict, process=process)
        if test_dictionary is not None:
            # Get test examples from the test dictionary
            example_list = self.get_test_examples(data=test_dictionary)
            # Create and return tests using the examples if any
            if self.create_tests(examples=example_list) is not None:
                return self.create_tests(examples=example_list)
        # Initialize a default Tests object if no examples are found
        tests = self.gxtp.Tests()
        test_a = self.gxtp.Test()
        # Add a default test parameter
        param = self.gxtp.TestParam(name="response", value="document")
        test_a.append(param)
        # Add default test outputs
        for output_name in self.output_name_list:
            name = f"{self.output_data}_{output_name}"
            output = self.gxtp.TestOutput(name=name, ftype="txt", value=f"{name}.txt")
            test_a.append(output)

        tests.append(test_a)
        return tests

    # To do refactor code after discussion
    def create_tests(self, examples):
        """
        Create tests from the given examples.

        This method initializes a Tests object and populates it with tests
        created from the provided examples.

        Args:
            examples (list): A list of example dictionaries used to create tests.

        Returns:
            Tests: A Tests object populated with the created tests.
        """
        tests = self.gxtp.Tests()

        for ex in examples:
            test = self.gxtp.Test()
            inputs = ex.get("inputs", {})
            outputs = ex.get("outputs", {})
            response = ex.get("response", "")

            self.add_test_response_param(test, response)
            self.process_test_input_params(test, inputs)
            self.process_test_output_params(test, outputs, response)

            tests.append(test)
        return tests

    def add_test_response_param(self, test, response):
        """
        Add a response parameter to the test.

        Args:
            test (Test): The test object to which the parameter is added.
            response (str): The response value for the parameter.
        """
        test.append(self.gxtp.TestParam(name="response", value=response))

    def process_test_input_params(self, test, inputs):
        """
        Process and add input parameters to the test.

        Args:
            test (Test): The test object to which the input parameters are added.
            inputs (dict): A dictionary of input parameters.
        """
        for key, value in inputs.items():
            param = self.create_test_input_param(key, value)
            if param is None:
                return None
            test.append(param)

    def create_test_input_param(self, key, value):
        """
        Create an input parameter for the test.

        Args:
            key (str): The name of the input parameter.
            value: The value of the input parameter, which can be a list, dictionary, or other type.

        Returns:
            TestParam: A TestParam object for the input parameter.
        """
        if isinstance(value, list):
            lst = [i.get("href") for i in value]
            return self.gxtp.TestParam(name=key, value=lst)
        elif isinstance(value, dict):
            href = value.get("href")
            if href is None:
                return None
            return self.gxtp.TestParam(name=key, value=href)
        else:
            return self.gxtp.TestParam(name=key, value=value)

    def process_test_output_params(self, test, outputs, response):
        """
        Process and add output parameters to the test.

        Args:
            test (Test): The test object to which the output parameters are added.
            outputs (dict): A dictionary of output parameters.
            response (str): The response type to determine the format of the output parameter.
        """
        for key, value in outputs.items():
            param = self.create_test_output_param(key, value, response)
            test.append(param)

    def create_test_output_param(self, key, value, response):
        """
        Create an output parameter for the test.

        Args:
            key (str): The name of the output parameter.
            value: The value of the output parameter, which can include format information.
            response (str): The response type to determine the format of the output parameter.

        Returns:
            TestOutput: A TestOutput object for the output parameter.
        """
        name = f"{self.output_data}_{key}"
        if response == "raw":
            media_type = value["format"]["mediaType"].split("/")[-1]
            return self.gxtp.TestOutput(name=name, ftype=media_type, value=f"{name}.{media_type}")
        else:
            return self.gxtp.TestOutput(name=name, ftype="txt", value=f"{name}.txt")

    def get_test_examples(self, data):
        """
        Extract example values from a nested dictionary.

        This method retrieves all example values from a specific part of a nested
        dictionary, which are used for creating tests.

        Args:
            data (dict): The nested dictionary containing example values.

        Returns:
            list: A list of example values.
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
            if len(parts) > 2 and process == parts[2]:
                return api_dict[pro]
        return None

    # To do: What should I citate
    def create_citations(self):
        citations = self.gxtp.Citations()
        citations.append(self.gxtp.Citation(type="bibtex", value="."))
        return citations
