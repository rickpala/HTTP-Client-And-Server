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
1. Take in cmd line arg as  "url:port/filename.html"
2. If file not yet cached, use HTTP GET to fetch file
    - Print contents
    - Cache the file
3. If file is cached, use Conditional GET
    - If not modified since last downloaded, print output saying so (no contents)
    - Else, Print and cache new contents

"""
def unpack_response(buffer):
    # Unpack short int, which is the length of the HTTP Req
    headers_size_in_B = struct.unpack("!h", buffer[:2])[0]
    headers = struct.unpack(f"!{headers_size_in_B}s", buffer[2:])[0]
     
    # Return headers as string
    return headers.decode()

def get_status_code(headers):
    # Status code is 1-th element on the request line
    request_line = headers.splitlines()[0]
    return request_line.split()[1]

def get_updated_mtime(headers):
    for line in headers.splitlines():
        if line.lower().startswith("last-modified"):
            # Return the modified time as a datetime obj
            search = re.search("last-modified: (.*)", line, re.IGNORECASE)
            last_mod_time_str = search.group(1)

            return last_mod_time_str

    # Shouldn't get here
    return None

def read_file_to_cache(file):
    cache = {}
    with open('cache.json', 'r') as f:
        try:
            cache = json.load(f)
        except ValueError:
            cache = {}

    return cache

def write_cache_to_file(cache):
    with open('cache.json', 'w') as f:
        json.dump(cache, f)

# Process cmdn line args
if len(sys.argv) == 2:
    full_url = sys.argv[1]
    search   = re.search('(.*):(.*)/(.*)', full_url)
    ip       = search.group(1)
    port     = search.group(2)
    url      = search.group(3)
else:
    print("URL not specified")
    quit()

# Establish TCP connection with host
client = socket.create_connection((ip, port), timeout=1)

# Read in and populate cache into dict (if exists)
cache = {}
cache_filename = "cache.json"
if os.path.exists(cache_filename):
    cache = read_file_to_cache(cache_filename) 


headers  = f"GET {url} HTTP/1.1\r\n"
headers += f"Host: {ip}:{port}\r\n"

cached = False
if url in cache:
    cached = True
    # Append Conditional GET headers
    modified_time = cache[url] 
    headers += f"If-modified-since: {modified_time}\r\n" 

headers += f"\r\n"
headers_size_in_B = len(headers.encode('utf-8')) 
bytes = struct.pack(f"!h{headers_size_in_B}s", headers_size_in_B, headers.encode())
print(headers) # KEEP
client.sendall(bytes)
 
buffer, address = client.recvfrom(1024)
res = unpack_response(buffer)

# Refresh cache according to last-modified time in response, if needed
status_code = get_status_code(res)
if status_code == "200":
    # Update cache with new mtime
    cache[url] = get_updated_mtime(res)

elif status_code == "304":
    pass

elif status_code == "404":
    # Remove from cache
    if cached:
        del cache[url]
     
write_cache_to_file(cache)

# Print contents
print(res) # KEEP

