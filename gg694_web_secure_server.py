#!/usr/bin/env python3
# A simple web server

import argparse
import ssl
import sys
import itertools
import socket
import http
from socket import socket as Socket
# imports the necessary libraries for the program


def main():
    # This line starts the main function.
    # Command line arguments. Use a port > 1024 by default so that we can run
    # without sudo, for use as a real server you need to use port 80.
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', default=2080, type=int,
                        help='Port to use')
    args = parser.parse_args()
    # These lines set up an argument parser and parse the arguments passed to the program.
    # The program takes a --port argument, which specifies the port to use for the server. The default port is 2080.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('server-public-key.pem', "server-private-key.pem")
    # These lines create an SSL context for the server using the ssl.SSLContext class. The server is
    # set to use the PROTOCOL_TLS_SERVER protocol, and the SSL certificate and private key are loaded
    # from files named ca-public-key.pem and ca-private-key.pem, respectively.
    # Create the server socket (to handle tcp requests using ipv4), make sure
    # it is always closed by using with statement.
    with Socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # This line creates a TCP/IP socket using the socket.socket function and wraps it in the Socket class.
        # The AF_INET parameter specifies the address family to use (IPv4),
        # and the SOCK_STREAM parameter specifies the socket type to use (TCP).
        # The socket is then assigned to the server_socket variable and opened within a with block.
        # The socket stays connected even after this script ends. So in order
        # to allow the immediate reuse of the socket (so that we can kill and
        # re-run the server while debugging) we set the following option. This
        # is potentially dangerous in real code: in rare cases you may get junk
        # data arriving at the socket.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # This line sets a socket option to allow reuse of the socket address.
        server_socket.bind(('', args.port))
        server_socket.listen(1)
        # These lines bind the socket to the specified port and start listening for
        # incoming connections. The listen function sets the number of queued connections to 1.
        print("server ready")
        # This line prints a message to indicate that the server is ready to accept connections.
        with context.wrap_socket(server_socket, server_side=True) as s:
           # This line wraps the server_socket in an SSL/TLS socket using the wrap_socket method
            # of the SSL context. The server_side parameter is set to True to indicate that the server is the SSL/TLS endpoint.
            while True:
                with s.accept()[0] as connection_socket:
                    # These lines wait for incoming connections, accept them using the accept method of the socket object,
                    # and assign the resulting connection socket to the connection_socket variable. The accept method blocks until a connection is received.
                    # This is a hackish way to make sure that we can receive and process multi
                    # line requests.
                    request = ""
                    received = connection_socket.recv(1024).decode('utf-8')
                    request += received
                    # These lines initialize a request variable to an empty string, receive data from the connection socket using the recv method
                    # decode the received data from bytes to a UTF-8 string, and append the decoded data to the request variable.
                    reply = http_handle(request)
                    connection_socket.sendall(reply.encode('utf-8'))
                    # These lines call
                print("\n\nReceived request")
                print("======================")
                print(request.rstrip())
                print("======================")
                # These lines simply print out the received request from the client socket connection.
                print("\n\nReplied with")
                print("======================")
                print(reply.rstrip())
                print("======================")
                # These lines print out the reply sent back to the client socket connection.

    return 0


def http_handle(request_string):
    """Given a http requst return a response

    Both request and response are unicode strings with platform standard
    line endings.
    """

    data = 'HTTP/1.1 200 OK\n'
    data += 'Connection: keep-alive\n'
    data += 'Content-Type: text/html; encoding=utf-8\n\n'
    f = open('index.html', 'r')
    # send data per line
    for l in f.readlines():
        data += l
    f.close()
    data += "\r\n\r\n"
    # This code reads the content of the "index.html" file and appends it to the data variable.
    # This variable will be used to send the response back to the client.
    req = request_string[:request_string.find('\r')]
    req = req.split(" ")
    req_dic = {'METHOD': req[0], 'URL': req[1], 'VERSION': req[2]}
    # These lines parse the request string and create a dictionary containing the request method, URL, and HTTP version.
    http_methods = ['GET', 'POST', 'HEAD', 'PUT',
                    'DELETE', 'CONNECT', 'OPTIONS', 'TRACE']

    if req_dic['METHOD'] not in http_methods or ('http' not in req_dic['VERSION'] and 'HTTP' not in req_dic['VERSION']):
        data = 'HTTP/1.1 400 Bad Request\r\n\r\n'

    elif req_dic['METHOD'] != "GET":
        data = 'HTTP/1.1 501 Not Implemented\r\n\r\n'

    elif req_dic['VERSION'] != 'HTTP/1.1' and req_dic['VERSION'] != 'http/1.1':
        data = 'HTTP/1.1 505 Version Not Supported\r\n\r\n'

    elif req_dic['URL'] == '/' or req[1] == '/index.html':
        return data

    else:
        data = "HTTP/1.1 404 Not Found\r\n\r\n"
    # These lines check the request method, version, and URL to determine the appropriate HTTP response code. If the request method is not recognized or the version is not supported,
    # a 400 or 505 response is sent. If the requested URL is "/" or "/index.html", the contents of the "index.html" file are returned. Otherwise, a 404 response is sent.
    return data
    # This line returns the HTTP response data to the caller of the http_handle function.
    # assert not isinstance(request_string, bytes)

    # Fill in the code to handle the http request here. You will probably want
    # to write additional functions to parse the http request into a nicer data
    # structure (e.g., not a string) and to easily create http responses.

    # Used Figure 2.8 in book as guideline: Request line and Header lines
    # Step 0: Split the string by line
    # Step 1: Get the first line (request line) and split into method, url, version
    # Step 2: Until you see <CR><LF> (\r\n), read lines as key, value with header name and value. Store as a dictionary
    # Step 3: Check to make sure method, url, and version are all compliant
    # Step 3a: if method is a GET and url is "/" or "/index.html" and correct HTTP version, we need to respond with 200 OK and some HTML
    # Step 3b: If method is compliant, but not implemented, we need to respond with a correct HTTP response
    # Step 3c: If the version is not compliant, we need to respond with correct HTTP response
    # Step 3d: If file does not exist in server path, respond with HTTP 404 File not found response
    # Step 4: Checking to make sure headers are correctly formatted

    raise NotImplementedError

    pass


if __name__ == "__main__":
    sys.exit(main())
# is a function that terminates the program, and its argument is used as the exit status.
