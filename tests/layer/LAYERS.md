# Test layers

Tests are organized in layers. The next layer uses the api from the previous one.

- layer 1 - http server
  - half-duplex communication aka http-requests/http-response

- layer 2 - resources
  - Resource represents something (a file) to be transferred
  - from_filesystem(...) returns an Iterable[PathResource]
  - library_resources() returns the library itself
  - define the user resources to be sent
    - locate/guesstimate the user files/folders
    - ... todo investigate better ways to do it
      - ; see python packages: modulefinder
      - <https://docs.python.org/3/library/modules.html>
      - <https://docs.python.org/3/glossary.html#term-finder>

  - build_archive(Iterator[Resource]) returns the bytes of a zip archive

- layer 3 - remote code execution; playwright needed from here on
  - plain python code remote execution - pyodide
  - bootstrap_routes(...) deliver zipped python files and execute them
    - zip_route to serve an application/zip
    - bootstrap_route to serve an html file that
      - bootstrap pyodide with the following python
      - download the zip, uncompress it, add to sys path, execute some main()
      - ... docs; limited lib support: wwwpy is not available, only pyodide
- layer 4 - convention(s)
- layer 5 - test client/server communication
  - half-duplex rpc using http-request/http-response coms
  - full-duplex rpc using websockets/long-polling coms
  - full-duplex communication aka websocket/long-polling
- layer 6 - higher level functionality
  - ask browser to refresh
 
Tests should be executed on all supported web servers.