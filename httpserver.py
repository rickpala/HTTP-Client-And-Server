# Ricky Palaguachi
# rsp84
# CS 356 - 007

import sys
import socket
import string
import random
import struct
import os
import re
import json
from datetime import datetime
import time

HTTP_DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"

"""
1. Take in cmd line args as "IP" "port"
2. Open a TCP socket and listen for incoming HTTP Get and Conditional GET
3. if HTTP GET:
    read named file and respond, including last-modified header
3. if Cond GET:
    if not modified:
        return Not Modified
    else if modified:
        update last-modified header
4. If file does not exist, return 404
5. Ignore any HTTP headers it does not understand

"""



# Get the server IP, port, and hostname 
if len(sys.argv) == 3:
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
else:
    server_ip = "127.0.0.1"
    server_port = 12001 

def unpack_headers(buffer):
    # Unpack short int, which is the length of the HTTP Req
    headers_size_in_B = struct.unpack("!h", buffer[:2])[0]
    headers = struct.unpack(f"!{headers_size_in_B}s", buffer[2:])[0]
   
    # Return headers as string
    return headers.decode()

def extract_url_from_headers(headers):
    # URL is 1-th element on the request line
    request_line = headers.splitlines()[0]
    return request_line.split()[1]

def find_last_mod_time(headers):
    # Find the Conditional GET line 
    for line in headers.splitlines():
        if line.lower().startswith("if-modified-since:"):
            # Return the modified time as a datetime obj
            search = re.search("if-modified-since: (.*)", line, re.IGNORECASE)  
            last_mod_time_str = search.group(1)

            return last_mod_time_str

    # No "if-modified-since" header found
    return None

def get_404_headers_as_bytes():
    current_datetime = \
        datetime.strftime(datetime.utcnow(), HTTP_DATETIME_FORMAT)

    res  =  "HTTP/1.1 404 Not Found\r\n"         
    res += f"Date: {current_datetime}\r\n"
    res += f"Content-Length: 0\r\n"
    res +=  "\r\n"
    print(res)

    res_size_in_B = len(res.encode())
    bytes = struct.pack(f"!h{res_size_in_B}s", res_size_in_B, res.encode())
    return bytes

def get_304_headers_as_bytes():
    current_datetime = \
        datetime.strftime(datetime.utcnow(), HTTP_DATETIME_FORMAT)

    res  =  "HTTP/1.1 304 Not Modified\r\n"
    res += f"Date: {current_datetime}\r\n"
    res +=  "\r\n"
    print(res)

    res_size_in_B = len(res.encode())
    bytes = struct.pack(f"!h{res_size_in_B}s", res_size_in_B, res.encode())
    return bytes


# Inititalize socket to listen for DNS request
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((server_ip, server_port))
print(f"The server is ready to receive on port: {server_port}")

# Listen for incoming connections
serverSocket.listen(1)

while True:

    # Wait for a connection
    print("Waiting for a request...")
    connection, address = serverSocket.accept()

    try:
        # Receive and unpack HTTP request
        buffer, address = connection.recvfrom(1024)
        headers = unpack_headers(buffer)
        requested_url = extract_url_from_headers(headers)
        
        print("Responding with...")

        # Determine if the file exists
        if requested_url not in os.listdir():
            # Send 404 Not Found
            bytes = get_404_headers_as_bytes()
            connection.sendall(bytes)
            continue # Await next request 
        
        # Send 304 Not Modified if applicable
        last_mod_time = find_last_mod_time(headers)
        
        # Obtain formatted local mod time
        secs = os.path.getmtime(requested_url)
        t = time.gmtime(secs)
        local_mod_time = time.strftime(HTTP_DATETIME_FORMAT, t)
        

        if last_mod_time is not None:
            modified = last_mod_time != local_mod_time

            if not modified:
                # Send 304 Not Modified
                bytes = get_304_headers_as_bytes()
                connection.sendall(bytes)
                continue

        # Send 200 OK 
        with open(requested_url, 'r') as file:
            current_datetime = \
                datetime.strftime(datetime.utcnow(), HTTP_DATETIME_FORMAT)
            contents = file.read()
            contents_size_in_B = len(contents.encode())
            

            res  =  "HTTP/1.1 200 OK\r\n"
            res += f"Date: {current_datetime}\r\n" 
            res += f"Last-modified: {local_mod_time}\r\n"
            res += f"Content-Length: {contents_size_in_B}\r\n"
            res += f"\r\n"
            res += f"{contents}" 

            res_size_in_B = len(res.encode())

            bytes = struct.pack(f"!h{res_size_in_B}s", res_size_in_B, res.encode())
            
            print(res)

            connection.sendall(bytes)
            continue

    finally:
        connection.close()

