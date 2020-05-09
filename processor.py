import re
import json
import base64
from core.internal import Internal, get_internal_methods
from termcolor import colored


class Processor(object):
    def __init__(self, component_definition: list, database_definition):
        try:
            super().__init__()
            self.class_manager = ClassManger()
            self.component_definition = component_definition
            self.database_definition = database_definition
        except Exception as error:
            raise Exception(f"Processor __init__ method error: {error}")

    def process_request(self, raw_data):
        try:
            request_data = json.loads(base64.b64decode(raw_data))
            print(
                f'[{colored("OK", "green")}][request_data] -> {request_data["request_id"]}'
            )
            current_request = Request(request_data["request_id"])

            for current_procedure_call in request_data["procedure_calls"]:
                for component in self.component_definition:
                    class_name = re.search("[.](.*)'>", current_procedure_call[0])
                    if component["name"] == class_name.group(1):
                        new_procedure_call = Procedure_call(
                            current_procedure_call[1], current_procedure_call[2]
                        )
                        class_id = re.search(
                            "<class at '(.*)[.]", current_procedure_call[0]
                        )
                        if class_id.group(1):
                            class_instance = self.class_manager.get_class_instance(
                                class_id.group(1), component
                            )
                            new_procedure_call.define_class(
                                component["name"], class_instance, class_id.group(1)
                            )
                            new_procedure_call.define_database(
                                self.database_definition.get_default()
                            )
                            new_procedure_call.define_method(current_procedure_call[3])
                            new_procedure_call.define_attribute(
                                current_procedure_call[4]
                            )
                            new_procedure_call.define_request_object(current_request)
                            current_request.add_procedure_call(new_procedure_call)
            return current_request
        except Exception as error:
            raise Exception(f"Process_request method error: {error}")


class Request(object):
    def __init__(self, id):
        super().__init__()
        self.__id = id
        self.__procedure_call_list = []

    def get_request(self):
        result_list = []
        for procedure_call in self.__procedure_call_list:
            result_list.append(procedure_call.get_procedure_call_object())
        return {
            "procedure_calls": result_list,
            "request_id": str(self.__id),
        }

    def get_procedure_call_objects(self):
        return self.__procedure_call_list

    def get_procedure_call_list_by_index(self, index):
        return self.__procedure_call_list[index]

    def add_procedure_call(self, procedure_call):
        self.__procedure_call_list.append(procedure_call)


class Procedure_call(object):
    def __init__(self, name, type):
        super().__init__()
        self.name = name
        self.type = type

    def get_value(self):
        return self.value

    def get_procedure_call_object(self):
        return [self.value]

    def define_class(self, name, instance, _id):
        self.class_name = name
        self.class_instance = instance
        self.class_id = _id

    def define_method(self, parameters):
        self.parameters = parameters

    def define_attribute(self, value):
        self.value = value

    def define_request_object(self, request_object):
        self.request_object = request_object

    def define_database(self, database):
        self.database = database

    def is_internal_method(self, method_name):
        for internal_method_name in get_internal_methods():
            if internal_method_name == method_name:
                return True
        return False

    def find_by_pointer(self, pointer):
        pointer_pattern = re.search("<pointer at (.*)>", str(pointer))
        if pointer_pattern:
            if pointer_pattern.group(1):
                return self.request_object.get_procedure_call_list_by_index(
                    int(pointer_pattern.group(1))
                ).get_value()

    def call(self):
        if self.type == "method":
            # NOTE: I don't understand why i can't assign pointer_value to parameter
            pointerless_parameter = []
            for parameter in self.parameters:
                pointer_value = self.find_by_pointer(parameter)
                if pointer_value:
                    pointerless_parameter.append(pointer_value)
                else:
                    pointerless_parameter.append(parameter)
            self.parameters = pointerless_parameter

            if self.is_internal_method(self.name):
                internal_class = Internal(
                    self.class_instance, self.database, self.class_name
                )
                self.value = getattr(internal_class, self.name)(self.parameters)
                # print("[Procedure_call][call][value] -> ", self.value)
            else:
                self.value = getattr(self.class_instance, self.name)(self.parameters)
        else:
            pointer_value = self.find_by_pointer(self.value)
            if pointer_value:
                self.value = pointer_value
            setattr(self.class_instance, self.name, self.value)


class ClassManger(object):
    def __init__(self):
        super().__init__()
        self.__class_list = []

    def get_class_instance(self, id, component):
        for current_class in self.__class_list:
            if current_class["id"] == id:
                return current_class["instance"]

        new_class = {"id": id, "instance": component["class"]()}
        self.__class_list.append(new_class)
        return new_class["instance"]
