# HTTP Client and Server

This repository contains two programs:

1. A client 

Sends an HTTP Server GET Requests for a file located
at a specified URL. Similar to a web browser search bar, except
DNS resolution is not currently supported. Recently updated web
pages are cached for efficiency.

2. A server

The server listens for GET Requests using TCP. The client's requests 
is handled as such:

* 200 OK - If requested URL available. Send back file contents.
* 304 Not Modified - If request headers contain "If-modified-since" and
server's version is not more up-to-date.
* 404 Not Found - If requested URL could not be found.


![Image of Program Execution](https://github.com/rpalaguachi/HTTP-Client-And-Server/blob/main/http-output.pdf)

