import re
import uuid


class _Method:
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))

    def __call__(self, *args):
        return self.__send(self.__name, args)


class RemoteClass(object):
    def __init__(self, class_name: str, request):
        self.class_name = class_name
        self.request = request
        self.class_id = f"<class at '{uuid.uuid1()}.{class_name}'>"

    def __request(self, methodname, params):
        if methodname == "setattr":
            return self.append_procedure_call(
                {
                    "i": str(uuid.uuid1()),
                    "c": self.class_id,
                    "n": params[0],
                    "t": "attribute",
                    "p": None,
                    "v": params[1],
                }
            )
        if methodname == "getattr":
            procedure_call_list = self.request.get_procedure_call_list()
            for procedure_call in procedure_call_list:
                if procedure_call["n"] == params[0]:
                    pointer_pattern = re.search(
                        "<pointer at (.*)>", str(procedure_call["v"])
                    )
                    if pointer_pattern:
                        if pointer_pattern.group(1):
                            return procedure_call_list[int(pointer_pattern.group(1))]["v"]
        else:
            return self.append_procedure_call(
                {
                    "i": str(uuid.uuid1()),
                    "c": self.class_id,
                    "n": methodname,
                    "t": "method",
                    "p": list(params),
                    "v": None,
                }
            )

    def append_procedure_call(self, procedure_call):
        self.request.add_procedure_call(procedure_call)
        return f"<pointer at {len(self.request.get_procedure_call_list()) - 1}>"

    def __getattr__(self, name):
        return _Method(self.__request, name)


class Request:
    def __init__(self, _id=None):
        if _id:
            self.__id = str(_id)
        else:
            self.__id = str(uuid.uuid1())
        self.__procedure_call_list = []
        self.__is_resolver = True

    def get_id(self):
        return self.__id

    def get_procedure_call_list(self):
        return self.__procedure_call_list

    def get_parent_procedure_call_id(self):
        return self.__parent_procedure_call_id

    def get_is_resolver(self):
        return self.__is_resolver

    def set_is_resolver(self, is_resolver: bool):
        self.__is_resolver = is_resolver

    def set_parent_procedure_call_id(self, parent_procedure_call_id: str):
        self.__parent_procedure_call_id = parent_procedure_call_id

    def set_procedure_call_value(self, index, value):
        self.__procedure_call_list[index]["v"] = value

    def set_continue(self, continue_method):
        self.__continue_method = continue_method

    def continue_request(self, request_response=None):
        if self.__is_resolver:
            return self.__continue_method()
        else:
            if request_response:
                return self.__continue_method(request_response)
            else:
                # TODO error if request_response not found
                pass

    def add_procedure_call(self, procedure_call):
        self.__procedure_call_list.append(procedure_call)

    def get_dict(self):
        return {
            "procedure_calls": self.__procedure_call_list,
            "request_id": self.__id,
        }


unresolved_request_list = []


class RequestManager:
    def __init__(self):
        pass

    def resolve_request(self, request_response):
        for unresolved_request in unresolved_request_list:
            if request_response["request_id"] == unresolved_request.get_id():
                if unresolved_request.get_is_resolver():
                    for unresolved_index, unresolved_procedure_call in enumerate(
                        unresolved_request.get_procedure_call_list()
                    ):
                        for index, procedure_call in enumerate(
                            request_response["procedure_calls"]
                        ):
                            if unresolved_procedure_call["t"] == "method":
                                if unresolved_procedure_call["i"] == procedure_call["i"]:
                                    unresolved_request.set_procedure_call_value(
                                        unresolved_index,
                                        procedure_call["v"],
                                    )
                    return {
                        "request_id": request_response["request_id"],
                        "procedure_calls": unresolved_request.continue_request(),
                    }
                else:
                    return {
                        "request_id": request_response["request_id"],
                        "procedure_calls": [
                            {
                                "i":unresolved_request.get_parent_procedure_call_id(),
                                "v":unresolved_request.continue_request(
                                    request_response["procedure_calls"]
                                ),
                            }
                        ],
                    }

    def generate_request(self, _id=None):
        return Request(_id)

    def set_resolver(self, request: Request, continue_method=None):
        if continue_method:
            request.set_continue(continue_method)
        unresolved_request_list.append(request)
        return request.get_dict()

    def compute_resolve(
        self, parent_procedure_call_id: str, request: Request, continue_method
    ):
        request.set_parent_procedure_call_id(parent_procedure_call_id)
        request.set_continue(continue_method)
        request.set_is_resolver(False)
        unresolved_request_list.append(request)
        return request.get_dict()


if __name__ == "__main__":
    manager = RequestManager()
    shop_request = manager.generate_request()
    shop = RemoteClass("Shop", shop_request)
    images = RemoteClass("Images", shop_request)

    shop.setattr("shop_result", shop.get({"name": "pep"}))
    images.setattr("image_result", images.get(shop.getattr("shop_result")))

    print(shop_request.get_procedure_call_list())
