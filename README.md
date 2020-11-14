# HTTP Client and Server

This repository contains two programs:

* A client 
that sends an HTTP Server GET Requests for a file located
at a specified URL. Similar to a web browser search bar, except
DNS resolution is not currently supported. Recently updated web
pages are cached for efficiency.

* A server
The server listens for GET Requests using TCP, and sends back the
contents of a file that the client requests.


![Image of Program Execution]
(http-output.pdf)
