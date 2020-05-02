import json
import base64
from core.databases import Databases
from core.processor import Processor
from core.file_loader import get_json


class Vachellia(object):
    def __init__(self, application_definition_file):
        try:
            super().__init__()
            application_definition = self.define_component(application_definition_file)
            database_definition = Databases(application_definition["databases"])
            self.processor = Processor(
                application_definition["components"], database_definition
            )
        except Exception as error:
            raise Exception(f"Vachellia __init__ method error: {error}")

    def import_class(self, path: str):
        try:
            components = path.split(".")
            mod = __import__(components[0])
            for comp in components[1:]:
                mod = getattr(mod, comp)
            return mod
        except:
            return None

    def define_component(self, definition):
        try:
            if "components" in definition:
                for component in definition["components"]:
                    new_class = self.import_class(component["import_path"])
                    if new_class == None:
                        raise Exception(
                            f'Import path not found: {component["import_path"]}'
                        )
                    else:
                        component["class"] = new_class
                return definition
            else:
                # TODO: error if not component definition.
                pass
        except Exception as error:
            raise Exception(f"define_component method error: {error}")

    def operate_request(self, raw_data):
        try:
            request = self.processor.process_request(raw_data)
            for procedure in request.get_procedure_call_objects():
                procedure.call()
            return base64.b64encode(json.dumps(request.get_request()).encode())
        except Exception as error:
            raise Exception(f"operate_request method error: {error}")
