#!/usr/bin/env python3
# This module defines general functions for establishing an arbitrary TCP connection with a remote host
from bs4 import BeautifulSoup
import socket
import ssl
import time

class HttpConnectionHelper:
    """
    Helper class for establishing a TCP connection
    """

    def __init__(self):
        """
        Constructor
        """
        self.internal_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port=80, secure=False):
        """
        Establishes a connection
        :return:
        """
        connection_port = port
        if secure:
            connection_port = 443
        self.internal_connection.connect((host, connection_port))
        if secure:
            self.internal_connection = ssl.wrap_socket(self.internal_connection, keyfile=None, certfile=None,
                                                       server_side=False, cert_reqs=ssl.CERT_NONE,
                                                       ssl_version=ssl.PROTOCOL_SSLv23)

    def send_request(self, request):
        """
        Sends an arbitrary request
        :param request: The request to send (as text)
        :return:
        """
        if not request.endswith("\r\n\r\n"): #cheks if the request ends with \r\n\r\n
            request = request + "\r\n\r\n" #if not appends it to the end

        self.internal_connection.send(request.encode())

    def receive_response(self):
        """
        Waits and receives a response form the server
        :return:
        """
        return self.internal_connection.recv(4096).decode('utf-8')

    def close(self):
        """
        Closes the connection
        :return:
        """
        self.internal_connection.close()


def get_headers(response):
    headers = response.split("\r\n")  # split headers from the response by the rows 
    print("Headers recived from server:")
    #print headers as a key:value pair
    for head_content in headers:
        if head_content:
            print(head_content)


def get_links(response): #function to get the links from the server's response
    count = 0
    links = []
    for anchors in response.find_all("a"): #find all anchor tags
        count+= 1 #Number of link
        href = anchors.get("href") #get the href attribute from the anchor tag
        links.append(href)
        print(f"[{count}] Link {count} -> {href}")#printing the number of the link
    return links



if __name__ == "__main__": #main program execution
    

    while True: #endless cycle to get inputs from users multiple time
        select_link = None #for the inner cycle to work
        connection_helper = HttpConnectionHelper() #creating a socket
        connection_helper.connect("localhost", 80, False) #establish the connection with server on port 80
        connection_helper.send_request("GET /example HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n") #send a get request to the server
        response = connection_helper.receive_response() #parse the first response
        headers = get_headers(response) #extracting headers from first response 
        print("----------------------------------")
        response = connection_helper.receive_response() #receive the second response
        http_response_body = BeautifulSoup(response, 'html.parser') #parse the html file 
        print("Here is all the available links:\n")
        links = get_links(http_response_body) #dictionary of all available links
        
        print("Press 0 to exit")
        
        while select_link not in range(0,len(links)+1): #check if the selected link is correct
            try:
                select_link = int(input("")) #type the link
                if select_link == 0: #check if it iszero
                    break

                if select_link not in range(0,len(links)+1): #check if is in the right range
                    print("Select the link from the list above or 0 to exit")
            except: #catching errors
                print("Select the link from the list above or 0 to exit") 
                continue
        
            
            
        if select_link == 0: #check if the user wants to exit the browser
            break

        if select_link != 0:
            # Get the selected link
            link = "/link"+str(select_link)
            print(link)
            connection_helper.close() #closing an old connection
            connection_helper = HttpConnectionHelper() #creating a new socket
            connection_helper.connect("localhost", 80, False) #establish the connection with server on port 80 once again since it does not work when i am trying to send more then 1 request per connection established for some reason
            connection_helper.send_request(f"GET {link} HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")  # Send a GET request for the selected link
           
        
            response = connection_helper.receive_response() #receive a header of the response
            headers = get_headers(response) #getting the headers
            response = connection_helper.receive_response() #parsing a body of the responce(html file)
            response_body = BeautifulSoup(response,"html.parser") #make it readable
            print(response_body) #print it
            action = input("Press enter to go back:\n") #just for the program to look better
