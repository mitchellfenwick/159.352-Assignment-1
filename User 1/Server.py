import requests
import certifi
import json
from socket import *

# Listening port for the server
serverPort = 8082

# Create the server socket object
serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind the server socket to the port
serverSocket.bind(('', serverPort))

# Start listening for new connections
serverSocket.listen(1)

print('The server is ready to receive messages')

while 1:
    # Accept a connection from a client
    connectionSocket, addr = serverSocket.accept()

    ## Retrieve the message sent by the client
    request = connectionSocket.recv(1024).decode('UTF-8')

    # Extract the requested resource from the path
    method = request.split()[0]
    resource = request.split()[1].split("/")[1]
    params = request.split()[-1]

    if resource.endswith(".html"):
        f = open(resource, "rb")
        content = f.read()
        f.close()
        headers = "HTTP/1.1 200 OK\r\n Content-Type: text/html\r\n\r\n"
        if method == "POST":
            params = params.split("=")
            filename = params[0] + ".json"
            with open(filename, 'r') as f:
                data = json.load(f)
                



    # create HTTP response
    #response = "HTTP /1.1 200 OK\n\n" + response_value

    # send HTTP response back to the client
    final_response = headers.encode()
    final_response += content
    connectionSocket.send(final_response)

    # Close the connection
    connectionSocket.close()