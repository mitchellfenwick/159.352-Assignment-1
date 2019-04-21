from socket import *
import _thread

serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = 8080

serverSocket.bind(("", serverPort))

serverSocket.listen(5)
print('The server is running')


# Server should be up and running and listening to the incoming connections


def process(connectionSocket):
    try:
        # Receives the request message from the client
        message = connectionSocket.recv(1024)
        # Extract the path of the requested object from the message
        print(message)
        filename = message.decode(encoding='UTF-8').split()[1]
        print ('File name is: ' + filename)
        # Because the extracted path of the HTTP request includes
        # a character '/', we read the path from the second character
        f = open(filename[1:])
        # Store the entire content of the requested file in a temporary buffer
        outputdata = f.read()
        # Send the HTTP response header line to the connection socket
        response = "HTTP/1.1 200 OK\r\n\r\n"

        # Send the content of the requested file to the connection socket
        for i in range(0, len(outputdata)):
            response += outputdata[i]
        response += "\r\n";

        # Close the client connection socket
        connectionSocket.send(response.encode())
        connectionSocket.close()

    except (IOError, IndexError):  # Send HTTP response message for file not found
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        response += "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n"
        connectionSocket.send(response.encode())
        connectionSocket.close()

while True:
    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()
    # Clients timeout after 60 seconds of inactivity and must reconnect.
    connectionSocket.settimeout(60)
    # start new thread to handle incoming request
    _thread.start_new_thread(process, (connectionSocket,))

serverSocket.close()
