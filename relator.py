from bson.objectid import ObjectId


class Relator(object):

    def __init__(self, database, parent_name, child_name):
        super().__init__()
        self.parent_name = parent_name
        self.child_name = child_name
        self.collection = database.get_collection(f'{parent_name}_{child_name}')

    def get(self, parameters):
        try:
            result_list = []
            result = self.collection.find(parameters)
            for document in result:
                document["_id"] = str(document["_id"])
                result_list.append(document)
            return result_list
        except Exception as error:
            raise Exception(f"get method error: {error}")

    def post(self, parameters):
        try:
            result = self.collection.insert_one(parameters)
            return {"_id": result.inserted_id}
        except Exception as error:
            raise Exception(f"post method error: {error}")

    def put(self, parameters):
        try:
            _id = parameters["_id"]
            del parameters["_id"]
            result = self.collection.find_one_and_update(
                {"_id":  ObjectId(_id)}, {"$set": parameters}
            )
            return {"_id": str(result["_id"])}
        except Exception as error:
            raise Exception(f"put method error: {error}")

    def delete(self, parameters):
        try:
            result = self.collection.delete_one(
                {"_id":  ObjectId(parameters['_id'])}
            )
            if result.deleted_count > 0:
                return {"_id": parameters['_id']}
        except Exception as error:
            raise Exception(f"delete method error: {error}")

    def get_relationship(self, relationship_data_list):
        try:
            for relationship_data in relationship_data_list:
                if "_id" in relationship_data:
                    relationship_result = self.get(
                        {
                            f'{self.parent_name}_id': relationship_data["_id"]
                        }
                    )
                    relationship_data["--relationship_id--"] = []
                    for result in relationship_result:
                        if f'{self.child_name}_id' in result:
                            relationship_data["--relationship_id--"].append(result[f'{self.child_name}_id'])
            # print(
            #     f'[get_relationship][relationship_data_list] -> {relationship_data_list}'
            # )
        except Exception as error:
            raise Exception(f"get_relationship method error: {error}")

    def delete_relationship(self, relationship_data_list):
        try:
            for relationship_data in relationship_data_list:
                if "_id" in relationship_data:
                    relationship_result = self.get(
                        {
                            f'{self.parent_name}_id': relationship_data["_id"]
                        }
                    )
                    for result in relationship_result:
                        if f'{self.child_name}_id' in result:
                            relationship_data["--relationship_id--"] = result[f'{self.child_name}_id']
                            self.delete({"_id": result["_id"]})
            # print(
            #     f'[delete_relationship][relationship_data_list] -> {relationship_data_list}'
            # )
        except Exception as error:
            raise Exception(f"delete_relationship method error: {error}")

    def create_relationship(self, parent_id, child_id):
        try:
            return self.post(
                {
                    f'{self.parent_name}_id': parent_id,
                    f'{self.child_name}_id': child_id,
                }
            )
        except Exception as error:
            raise Exception(f"create_relationship method error: {error}")