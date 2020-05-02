# Vachellia core
<img src="assets/icons/Vachellia_core.png" width="200">

The Vachellia core is a functional APIs library. The library is a set of files responsible for the construction and processing of requests, interfacing of a database, basic crud operations and relation of requests objects.

## File Definition

- Processor - responsible for the processing of incoming requests by validating the requests' procedural calls against the defined Vachellia specification.

- Database - creating a database instance with functions to allow the application to interface with mongodb. 

- File loader - allow for the retrieval of json or yaml files.

- Internal - a conglomeration of internal functions built into the Vachellia core that an incoming request can interface.

- Relator - This allows the application to relate request result data.

- RPC Client - this module is responsible for the construction and  resolution of procedure calls.

## Glossary

- Vachellia Specification - a json file containing the structure of the applications' attributes and method manipulation.

- Cell - a single instance of a Vachellia application.

## License
Copyright (c) Future Envision Corporation. All rights reserved.

Licensed under the [Apache License](./LICENSE).