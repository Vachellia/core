import pymongo


class Databases(object):
    def __init__(self, databases_definition):
        # TODO: add more database support
        try:
            self.databases = []
            self.default_database: MongoDatabase = None
            for database_definition in databases_definition:
                if database_definition["type"] == "mongodb":
                    new_connection = MongoDatabase(
                        database_definition["name"], database_definition["url"]
                    )
                    self.databases.append(new_connection)
                    if "default" in database_definition:
                        if database_definition["default"] == True:
                            if self.default_database == None:
                                self.default_database = new_connection
                            else:
                                raise Exception(
                                    f"'Database Error: more than one database set at default"
                                )
        except Exception as error:
            raise Exception(f"databases __init__ method error: {error}")

    def get_default(self):
        try:
            if self.default_database == None:
                raise Exception(f"'Database Error: default database not found")
            return self.default_database
        except Exception as error:
            raise Exception(f"get_default method error: {error}")

    def get_all_database(self):
        try:
            return self.databases
        except Exception as error:
            raise Exception(f"get_all_database method error: {error}")


class MongoDatabase(object):
    def __init__(self, name, url):
        try:
            self.database_name = name
            self.mongo_client_url = url
            self.client = pymongo.MongoClient(self.mongo_client_url)
        except:
            raise Exception("Database Error: mongodb not configured")

    def get_collection(self, collection):
        try:
            return self.client[self.database_name][collection]
        except Exception as error:
            raise Exception(f"get_collection method error: {error}")
