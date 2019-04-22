import pycurl
import certifi
from socket import *
from io import BytesIO
import xml.etree.ElementTree as ET

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
    resource = request.split()[1].split("/")[1]

    # This is buffer to hold response from google map API server
    response_buffer = BytesIO()

    curl = pycurl.Curl()

    # Set the curl options which indentify the Google API server, the parameters to be passed to the API,
    # and buffer to hold the response
    curl.setopt(pycurl.CAINFO, certifi.where())
    curl.setopt(curl.URL,
                'https://maps.googleapis.com/maps/api/geocode/xml?key=AIzaSyAU0y5AGm-PdLrNhQAnARHFGj1fTuSLQ3s&address="' + resource + '"')
    curl.setopt(curl.WRITEFUNCTION, response_buffer.write)

    curl.perform()
    curl.close()

    response_value = response_buffer.getvalue().decode('UTF-8')
    if len(response_value) > 107:
        with open('responsexml.xml', 'wb') as file:
            file.write(response_value.encode('UTF-8'))
        tree = ET.parse('responsexml.xml')
        root = tree.getroot()
        location = root.find('./result/formatted_address')
        latitude = root.find('./result/geometry/location/lat')
        longitude = root.find('./result/geometry/location/lng')
        response_value = location.text + ' is located at Latitude ' + latitude.text + ' and Longitude ' + longitude.text
    else:
        response_value = 'No place found'

    # create HTTP response
    response = "HTTP /1.1 200 OK\n\n" + response_value

    # send HTTP response back to the client
    connectionSocket.send(response.encode())

    # Close the connection
    connectionSocket.close()