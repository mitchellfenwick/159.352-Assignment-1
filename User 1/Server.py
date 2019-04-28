
import requests
import requests_cache
import json
import datetime
import calendar
import _thread
from socket import *

# Listening port for the server
serverPort = 8082

# Create the server socket object
serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind the server socket to the port
serverSocket.bind(('', serverPort))

# Start listening for new connections
serverSocket.listen(5)

# Create a local cache file where responses are stored
requests_cache.install_cache(cache_name='github_cache', backend='sqlite', expire_after=60)

print('The server is ready to receive messages')
print(serverPort)

def process(connectionSocket, addr):
    try:
        # Accept a connection from a client
        ## Retrieve the message sent by the client
        request = connectionSocket.recv(1024).decode('UTF-8')
        if request != "":
            print(request)
            # Extract the requested resource, method and params from the path
            method = request.split()[0]
            resource = request.split()[1][1:]
            params = request.split()[-1]
            # Make sure resource is valid
            if resource != "":
                # Deal with POST method on update.html page
                if resource.endswith("update.html") and method == "POST":
                    params = params.split("=")
                    filename = params[0] + ".json"
                    # Open Status file so that it can be updated with new status
                    with open(filename, 'r') as f:
                        # Create new status
                        data = json.load(f)
                        timestamp = str(datetime.datetime.now().isoformat(' ', 'seconds'))
                        text = params[1].replace("+", " ")
                        likes = []
                        status = {'timestamp': timestamp, 'text': text, 'likes': likes}
                        data[params[0]].append(status)
                    # Write newly created status to status.json
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=4)
                # Deal with GET method on friends.html page
                if resource.endswith("friends.html") and method == "GET":
                    # Create html content that will be written to friends.html file
                    friends_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Friends</title>
    <link href="https://fonts.googleapis.com/css?family=Raleway:300,400" rel="stylesheet"> 
    <style>
        body {
            background: #108dc7; /* fallback for old browsers */
            background: -webkit-linear-gradient(to right, #108dc7, #ef8e38); /* Chrome 10-25, Safari 5.1-6 */
            background: linear-gradient(to right, #108dc7, #ef8e38); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
            text-align: center;
            font-family: 'Raleway', 'Lucida Sans';
        }

        img {
            margin: auto;
            border: 1px solid grey;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            width : 90%;
            height: auto;
        }
        
        .offline {
            font-weight: 300;
        }
        
        #likebutton {
            border: 1px solid #00a3cc;
            font-size: 1em;
            border-radius: 20px;
            width: 7em;
            height: 3em;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            margin-bottom: 2%;
            margin-top: 3%;
        }

        #likebutton:hover {
            background-color: #00a3cc;
        }

        #likebutton:active {
            background-color: #00b8e6;
        }
        
        #likebutton:disabled {
            background-color: #00a3cc;
        }
        
        .name {
            padding-top: 5%;
            font-weight: 400;
        }

        #img {
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
        }

        #form {
            margin-top: 1%;
        }
        
        #card {
            background-color: white;
            margin: auto;
            margin-bottom: 3%;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
        }
        
        #main {
            margin-top: 3%;
        }
        
        #status {
            font-weight: 400;
        }
        
        #details {
            font-weight: 300;
        }
        
        @media screen and (min-width: 1400px) {
            #card {
                width: 22%;
            }
        }

        @media screen and (min-width: 992px) and (max-width: 1400px) {
            #card {
                width: 42%;
            }
        }

        @media screen and (min-width: 768px) and (max-width: 992px) {
            #card {
                width: 62%;
            }
        }

        @media screen and (max-width: 768px) {
            #card {
                width: 82%;
            }
        }
    </style>
</head>
<body>
    <div id="main">"""
                    # Open friends.json file to get information on friends
                    with open('friends.json', 'r') as friends:
                        data = json.load(friends)
                        # Counter for appending to name of pictures that will later be stored on local disk
                        counter = 0
                        # Create a list of IP address that will be used to authenticate incoming request
                        accepted_IP = []
                        # Determine which IP addresses should be added to the list of accepted IP addresses
                        for person in data["Friends"]:
                            person_IP = person["IP"].split(":")[0]
                            accepted_IP.append(person_IP)
                        # Loop through the list of friends
                        for person in data["Friends"]:
                            # Validate that this is a trusted IP address
                            if addr[0] in accepted_IP:
                                # Create URL to request friends status.json file
                                url = "http://" + person['IP'] + "/status.json"
                                # Try to see if friend is online
                                try:
                                    # request friends status.json file
                                    r = requests.get(url)
                                    r_json = r.json()
                                    # Add on to the html content with friends name and picture
                                    friends_html += """
        <div id="card">
            <div>
                <h3 class="name">[Name]</h3>
                <img src="[Source]" alt="" id="img">
            </div>"""
                                    # Create URL to grab friends picture
                                    img_url = "http://" + person["IP"] + "/profile.jpg"
                                    img_request = requests.get(img_url)
                                    img_file = "CacheImages/profile" + str(counter) + ".jpg"
                                    # Save picture to local disk so that it can be accessed by the html page without
                                    # contacting the friend directly. Check if it is not cached first
                                    if img_request.from_cache != True:
                                        with open(img_file, 'wb') as img:
                                            img.truncate(0)
                                            img.write(img_request.content)
                                    # Increment picture counter
                                    counter += 1;
                                    # Replace html values with friends details
                                    friends_html = friends_html.replace("[Name]", person["name"])
                                    friends_html = friends_html.replace("[Source]", img_file)
                                    # Try see if friend has a status, if not then skip
                                    try:
                                        # Get most recent status
                                        status = r_json["Status"][-1]
                                        # Add onto html content with status
                                        friends_html += """
            <div>
                <h4 id="status">[Text]</h4>
                <p id="details">Time: [Time] | Likes: [Likes]</p>
                <form method = "POST" action="/friends.html">
                    <input type="hidden" name="StatusIndex" value="[0]" />
                    <input type="hidden" name="IPAddr" value="[1]" />
                    <input type="hidden" name="ID" value="[2]" />"""
                                        # Check to see if user has already liked status
                                        # If yes add a disabled button
                                        # If no add an enabled button
                                        my_ip = "127.0.0.1:" + str(serverPort)
                                        if my_ip in status['likes']:
                                            friends_html += """
                    <button type="submit" id="likebutton" disabled>Like</button>     
                </form>    
            </div>
        </div>"""
                                        else:
                                            friends_html += """
                    <button type="submit" id="likebutton">Like</button>     
                </form>    
            </div>
        </div>"""
                                        # replace values in html content with friends status details
                                        friends_html = friends_html.replace("[0]", '-1')
                                        friends_html = friends_html.replace("[1]", addr[0])
                                        friends_html = friends_html.replace("[2]", person["ID"])
                                        friends_html = friends_html.replace("[Text]", status["text"])
                                        friends_html = friends_html.replace("[Time]", status["timestamp"])
                                        friends_html = friends_html.replace("[Likes]", str(len(status["likes"])))
                                    # if firend has no status
                                    except:
                                        friends_html += """
        </div>"""
                                # If friend is offline
                                except:
                                    friends_html += """
        <div>
            <h3 class="name">[Name]</h3>
            <h3 class="offline">Offline</h3>
        </div>"""
                                    friends_html = friends_html.replace("[Name]", person["name"])
                            # If the request is made by someone not in the list of accepted IP addresses
                            else:
                                friends_html += """
        <div>
            <h3 id="name">Unknown Person</h3>
        </div>"""
                        # Close of the html content
                        friends_html += """
    </div>
</body>
</html>"""
                    # Write html content to friends.html file
                    with open('friends.html', 'w+') as file:
                        file.truncate(0)
                        file.write(friends_html)

                # Deal with POST method on friends.html page
                if resource.endswith("friends.html") and method == "POST":
                    # Clear the cache so that new likes are shown
                    requests_cache.clear()
                    # Extract parameters from request
                    old_params = params.split("&")
                    new_params = []
                    for param in old_params:
                        old_param = param.split("=")
                        new_params.append(old_param)
                    # Open friends.json file to let a friend know their post has been liked
                    with open('friends.json', 'r') as friends:
                        data = json.load(friends)
                        for person in data["Friends"]:
                            # Sort which like button was pressed
                            if person['ID'] == new_params[2][1]:
                                # Build parameters to send to friend
                                params_to_send = {new_params[0][0]: new_params[0][1], new_params[1][0]: new_params[1][1], "Port": str(serverPort)}
                                url_to_send = "http://" + person["IP"] + "/status.json"
                                # Send POST request to friend so they can update thier status file with the new like
                                requests.post(url_to_send, params=params_to_send)
                    # Request friends.html page again to refresh and update likes
                    requests_url = "http://127.0.0.1:" + str(serverPort) + "/friends.html"
                    requests.get(requests_url)

                # Deal with POST request on status.json to update likes
                if resource.startswith("status.json") and method == "POST":
                    # Extract parameters from request
                    params = resource[12:]
                    old_params = params.split("&")
                    new_params = []
                    for param in old_params:
                        old_param = param.split("=")
                        new_params.append(old_param)
                    # Open status file to be read and build new content
                    with open("status.json", 'r') as status:
                        data = json.load(status)
                        new_IP = new_params[0][1] + ":" + new_params[1][1]
                        if new_IP not in data["Status"][-1]['likes']:
                            data["Status"][-1]['likes'].append(new_IP)
                    # Open status file and write new content
                    with open("status.json", "w") as status:
                        json.dump(data, status, indent=4)

                # Set content to resource form request
                f = open(resource, "rb")
                content = f.read()
                f.close()
                # Change Content-Type header depending on resource requested
                if resource.endswith(".html"):
                    contentType = "text/html"
                elif resource.endswith((".png", ".jpg", ".ico")):
                    contentType = "image/" + resource.split('.')[-1]
                elif resource.endswith(".json"):
                    contentType = "application/json"
                # Build headers
                headers = "HTTP/1.1 200 OK\r\n"
                headers += "Content-Type:"+contentType+"\r\n"
                headers += "Access-Control-Allow-Origin: *\r\n"
                headers += "\r\n"


            # send HTTP response back to the client
            final_response = headers.encode()
            final_response += content
            connectionSocket.send(final_response)
            # Close the connection
            connectionSocket.close()

    # Send HTTP response message for file not found
    except (IOError, IndexError):
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        response += "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n"
        connectionSocket.send(response.encode())
        connectionSocket.close()

# Begin Loop
while 1:
    connectionSocket, addr = serverSocket.accept()
    connectionSocket.settimeout(60)
    _thread.start_new_thread(process, (connectionSocket,addr,))

# Close Socket when server is shutdown
serverSocket.close()