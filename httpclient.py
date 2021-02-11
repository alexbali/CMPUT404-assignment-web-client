#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    """
    Arguments: this function takes a variable called data which is the response returned from either a GET or POST request
    Return: the status code as an integer
    """
    def get_code(self, data):
        first_line = data.split("\n")
        first_line_split = first_line[0].split()
        return int(first_line_split[1])

    """
    Arguments: this function takes a variable called url which is the url being used
    Return: the path, port number, object o of urllib.parse
    """
    def parse_url(self, url):
        o = urllib.parse.urlparse(url)
        # check if path is empty
        path = o.path 
        if not o.path:
            path = "/"
        # check to see if there is a port specified
        port = o.port
        if not port:
            port = 80
        return path, port, o

    """
    Arguments: this function takes a variable called data which is the response returned from either a GET or POST request
    Return: the body of the response
    """
    def get_body(self, data):
        # print result of GET or POST to stdout
        print(data)
        split = data.split("\r\n\r\n")
        return(split[1])
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    """
    Arguments: this function takes a variable called url and any arguments present in the url
    Return: the HTTP response of the GET request
    GET Format: GET /path HTTP/1.1, Host, Accept, Connection
    """
    def GET(self, url, args=None):
        path,port,o = self.parse_url(url)
        self.connect(o.hostname, port)    
        req = f"GET {path} HTTP/1.1\r\nHost: {o.hostname}\r\nAccept: */*\r\nConnection: Closed\r\n\r\n"
        self.sendall(req)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.socket.close()
        return HTTPResponse(code, body)

    """
    Arguments: this function takes a variable called url and any arugments for the url
    Return: the HTTP response of the POST request
    POST Format: POST /path HTTP/1.1, HOST, Connection, Content-Length, Content
    """
    def POST(self, url, args=None):
        content = "Content-Type: application/x-www-form-urlencoded"
        path,port,o = self.parse_url(url)
        self.connect(o.hostname, port)
        req = ""
        # check if the post request will need a body sent with it
        if not args:
            req = f"POST {path} HTTP/1.1\r\nHost: {o.hostname}\r\nAccept: */*\r\nConnection: Closed\r\nContent-Length: {str(0)}\r\n{content}\r\n\r\n"
        else:
            # convert dictionary into query string
            req_body = urllib.parse.urlencode(args,doseq=True)
            print(req_body)
            size = str(len(req_body))
            req = f"POST {path} HTTP/1.1\r\nHost: {o.hostname}\r\nAccept: */*\r\nConnection: Closed\r\nContent-Length: {size}\r\n{content}\r\n\r\n{req_body}" 
        self.sendall(req)
        response = self.recvall(self.socket)
        self.socket.close()
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
