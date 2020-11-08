# This program is to provide functionality of FileServer node
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import os
import json
import time

# Initialize the file server by selecting the directory
file_server = ''
# Variable to store registration 
serverDetails={}


# Register the server with KDC
def registerFS():
    # Info of KDC
    number=8001
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{number}/")
    # Make isFileServer true here
    sendMessage=json.dumps({
        "id":None,
        "key":None,
        "isFileServer":True
    })
    kdcMessage=json.loads(proxy.registerFileServer(sendMessage))
    
    countFS=kdcMessage['countFS']
    print(os.popen(f'mkdir folder{countFS}'))
    time.sleep(0.1)
    global file_server
    file_server=f'folder{countFS}'

    # Store details to global variable
    global serverDetails
    serverDetails=kdcMessage
    print("saved my details")

# Check for valid command
def isValidCommand(command:str):
    a=max(  command.find('ls'),
            command.find('pwd'),
            command.find('cp'),
            command.find('cat'),
            command.find('close'))
    if(a==-1):
        return False
    return True

# Run the user command
def runCommand(command:str):
    if(isValidCommand(command)):
        if(command.find('pwd')!=-1):
            return f'/{file_server}'
        return os.popen(command).read()
    else:
        return f"Command '{command}' not found"


# Serve client node once Authenticated
def serveClient():
    port_num=int(input("Enter the port number"))
    server=SimpleXMLRPCServer(("localhost",port_num))
    print(f"listening on {port_num}...")

    # Register function
    server.register_function(runCommand,'runCommand')

    # start listening  on the given port 
    server.serve_forever()



registerFS()
print(serverDetails)

os.chdir(file_server)

print(os.popen('pwd').read())
# serveClient()

