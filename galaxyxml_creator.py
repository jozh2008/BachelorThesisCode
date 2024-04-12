
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
            format=unique_enum_values
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

    def create_params(self, inputs_json, outputs_json):
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
        
        self.create_output_param(output_json=outputs_json, inputs=inputs)

        return inputs

    def create_output_param(self,output_json, inputs):

        for item_number,(param_name, param_dict) in enumerate(output_json.items(), start=1):
            param_schema = param_dict.get("schema")
            param_extended_schema = param_dict.get("extended-schema")
            param_type = param_schema.get("type")
            param_name = "output_type_" + str(item_number)
            if param_type == "string":
                if param_schema.get("enum"):
                    param = self.create_select_param(param_name, param_dict)
                else:
                    param = self.create_text_param(param_name, param_dict)
            elif param_extended_schema is not None:
                param = self.create_select_param_output(param_name, param_dict, param_extended_schema)
            else:
                # Handle unsupported parameter types gracefully
                print(f"Warning: Parameter '{param_name}' with unsupported type '{param_type}'")
                continue
            inputs.append(param)
    
    def define_output_options(self):
        outputs = self.gxtp.Outputs()
        param = self.gxtp.OutputData(name="output_data", format="png")
        
        change = self.gxtp.ChangeFormat()
        change_a = self.gxtp.ChangeFormatWhen(input="output_type_1", value="tiff", format="tiff")
        change_b = self.gxtp.ChangeFormatWhen(input="output_type_1", value="jepg", format="jepg")
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
        param = self.gxtp.TestParam(name="output_type_1", value="png")
        output = self.gxtp.TestOutput(name="output_data", value="png")
        test_a.append(output)
        test_a.append(param)

        tests.append(test_a)
        return tests
    
    def create_citations(self):
        citations = self.gxtp.Citations()
        citations.append(self.gxtp.Citation(type="bibtex", value = "Josh"))
        return citations
