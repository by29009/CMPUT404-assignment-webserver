#  coding: utf-8 
import SocketServer
import socket
import os
import os.path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, by29009@gmail.com
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        request = self.request
        assert(isinstance(request, socket.socket))
        requestData = request.recv(4096)

        print ("######### Got a request #########\n{0}\n".format(requestData.strip()))

        httpRequest = requestData.strip().split('\n')[0]

        if httpRequest[:4] != 'GET ':
            self.request.sendall('400 Bad Request')
            print('Error: Only GET is supported')
            return

        if len(httpRequest.split(' ')) != 3:
            self.request.sendall('400 Bad Request')
            print('Error: Bad request (first line should have three parts)')
            return

        _, requestURL, httpVer = map(lambda x: x.strip(), httpRequest.split(' '))

        if requestURL[-1] == '/':
            expectFolder = True
        else:
            expectFolder = False

        if httpVer not in ['HTTP/1.0', 'HTTP/1.1']:
            self.request.sendall('400 Bad Request')
            print('Error: Bad HTTP ver')
            return

        pyPath = os.path.dirname(os.path.realpath(__file__))
        pyPath = os.path.join(pyPath, 'www')

        requestURL = os.path.normpath(requestURL)
        if requestURL[0] in ['\\', '/']:
            requestURL = requestURL[1:]

        requestPath = os.path.join(pyPath, requestURL)

        # print(pyPath)
        # print(requestPath)

        responseCode = '200 OK'

        if not os.path.exists(requestPath):
            print('404: {0}'.format(requestPath))
            responseCode = '404 Not Found'
            requestPath = os.path.join(pyPath, '404page.html')

        if not os.path.isfile(requestPath):
            if expectFolder:
                requestPath = os.path.join(requestPath, 'index.html')

            else:
                responseCode = '404 Not Found'
                requestPath = os.path.join(pyPath, '404page.html')

        requestPath = os.path.normpath(requestPath)
        absRequestPath = os.path.normpath(os.path.join(os.getcwd(), requestPath))
        if absRequestPath.find(pyPath) == -1:
            print('403: {0} {1}'.format(pyPath, absRequestPath))
            responseCode = '403 Forbidden'
            requestPath = os.path.join(pyPath, '403page.html')

        with open(requestPath, 'rb') as f:
            fileBuf = f.read()

        _, ext = os.path.splitext(requestPath)

        contentType = 'text'
        if ext == '.html':
            contentType = 'text/html'
        elif ext == '.css':
            contentType = 'text/css'

        response = httpVer + ' {0}\r\n'.format(responseCode)
        response += 'Cache-Control: no-cache\r\n'
        response += 'Content-Type: {0}; charset=utf-8\r\n'.format(contentType)
        response += 'Content-Length: {0}\r\n'.format(len(fileBuf))
        response += 'Connection: close\r\n'
        response += '\r\n'
        response += fileBuf
        response += '\r\n\r\n' # needed?

        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
