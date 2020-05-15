from bson.objectid import ObjectId
from core.relator import Relator
from termcolor import colored


class Internal(object):
    def __init__(self, class_instance, database, class_instance_name):
        try:
            super().__init__()
            self.class_instance = class_instance
            self.class_instance_name = class_instance_name
            self.database = database
            self.database_collection = database.get_collection(class_instance_name)
        except Exception as error:
            raise Exception(f"internal __init__ method error: {error}")

    # NOTE: it's possible to share a variable between the internal class and the component class
    # def get(self, parameters):
    #     print("[Internal][get][parameters] -> ", parameters)
    #     if parameters[0] == "result":
    #         print("[Shops][test][result] -> ", self.class_instance.result)

    def get(self, parameters):
        if len(parameters) == 1:
            results_list = []
            results = self.database_collection.find(parameters[0])

            for document in results:
                document["_id"] = str(document["_id"])
                results_list.append(document)

            return {
                "status": "success",
                "data": results_list,
                "class_name": self.class_instance_name,
            }
        elif len(parameters) == 2:
            relation = Relator(
                self.database, parameters[1]["class_name"], self.class_instance_name
            )
            relation.get_relationship(parameters[1]["data"])
            for relationship_data in parameters[1]["data"]:
                results_list = []
                if "--relationship_id--" in relationship_data:
                    results = self.database_collection.find(
                        {"_id": ObjectId(relationship_data["--relationship_id--"])}
                    )
                    for document in results:
                        document["_id"] = str(document["_id"])
                        results_list.append(document)

                    del relationship_data["--relationship_id--"]
                    relationship_data[self.class_instance_name] = results_list

            return {
                "status": "success",
                "data": parameters[1]["data"],
                "class_name": self.class_instance_name,
            }

    def create(self, parameters):
        if len(parameters) == 1:
            result = self.database_collection.insert_one(parameters[0])
            return {
                "status": "success",
                "data": {"_id": str(result.inserted_id)},
                "class_name": self.class_instance_name,
            }

        elif len(parameters) == 2:
            relation = Relator(
                self.database, parameters[1]["class_name"], self.class_instance_name
            )
            result = self.database_collection.insert_one(parameters[0])
            relationship = relation.create_relationship(
                parameters[1]["data"]["_id"], str(result.inserted_id)
            )
            if relationship != None:
                return {
                    "status": "success",
                    "data": {"_id": str(result.inserted_id)},
                    "class_name": self.class_instance_name,
                }

    def update(self, parameters):
        if len(parameters) == 1:
            _id = parameters[0]["_id"]
            del parameters[0]["_id"]
            result = self.database_collection.find_one_and_update(
                {"_id": ObjectId(_id)}, {"$set": parameters[0]}
            )

            return {
                "status": "success",
                "data": [{"_id": str(result["_id"])}],
                "class_name": self.class_instance_name,
            }

        elif len(parameters) == 2:
            relation = Relator(
                self.database, parameters[1]["class_name"], self.class_instance_name
            )
            relation.get_relationship(parameters[1]["data"])
            result_list = []
            for relationship_data in parameters[1]["data"]:
                if "--relationship_id--" in relationship_data:
                    if relationship_data["--relationship_id--"] == parameters[0]["_id"]:
                        del parameters[0]["_id"]
                        result = self.database_collection.find_one_and_update(
                            {"_id": ObjectId(relationship_data["--relationship_id--"])},
                            {"$set": parameters[0]},
                        )

                        del relationship_data["--relationship_id--"]
                        result_list.append({"_id": str(result["_id"])})
                    else:
                        pass
                        # TODO: allow put on unspecified id

            return {
                "status": "success",
                "data": result_list,
                "class_name": self.class_instance_name,
            }

    def delete(self, parameters):
        if len(parameters) == 1:
            result = self.database_collection.delete_one(
                {"_id": ObjectId(parameters[0]["_id"])}
            )

            if result.deleted_count == 1:
                return {
                    "status": "success",
                    "data": [{"_id": parameters[0]["_id"]}],
                    "class_name": self.class_instance_name,
                }
            else:
                # TODO: return error
                pass
        elif len(parameters) == 2:
            relation = Relator(
                self.database, parameters[1]["class_name"], self.class_instance_name
            )
            relation.delete_relationship(parameters[1]["data"])
            result_list = []
            for relationship_data in parameters[1]["data"]:
                if "--relationship_id--" in relationship_data:
                    if relationship_data["--relationship_id--"] == parameters[0]["_id"]:
                        result = self.database_collection.delete_one(
                            {"_id": ObjectId(parameters[0]["_id"])}
                        )
                        if result.deleted_count > 0:
                            result_list.append({"_id": parameters[0]["_id"]})
                        del relationship_data["--relationship_id--"]
                    else:
                        pass
                        # TODO: allow put on unspecified id

            return {
                "status": "success",
                "data": result_list,
                "class_name": self.class_instance_name,
            }


def get_internal_methods():
    return ["get", "create", "update", "delete"]
