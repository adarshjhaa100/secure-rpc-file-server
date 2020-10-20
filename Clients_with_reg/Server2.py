from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import os
import sys
import json
# File server id


# Registration of File Server
# number=input('Enter Port of KDC')
number = 8100
proxy = xmlrpc.client.ServerProxy(f"http://localhost:{number}/")

# Request kdc server to register FS


def registerServer(proxy):
    serverMessage = json.dumps({
        "id": None,
        "key": None,
        "isFileServer": True
    })
    print(serverMessage)

    kdcMessage = json.loads(proxy.registerFileServer(serverMessage))
    saveFsDetails(kdcMessage)

# Store the id and encryption key given


def saveFsDetails(kdcMessage):
    print(kdcMessage)
    print("saved my details")


registerServer(proxy)


# Point out to the folder of server
file_server = "FS2"
os.chdir(file_server)

# Check for valid command


def isValidCommand(command: str):
    a = max(command.find('ls'),
            command.find('pwd'),
            command.find('cp'),
            command.find('cat'),
            command.find('close'))
    if(a == -1):
        return False
    return True

# Run the user command


def runCommand(command):
    if(isValidCommand(command)):
        if(command.find('pwd') != -1):
            return f'/{file_server}'
        return os.popen(command).read()
    else:
        return f"Command '{command}' not found"


port_num = 8082
server = SimpleXMLRPCServer(("localhost", port_num))
print(f"listening on {port_num}...")

# Register function
server.register_function(runCommand, 'runCommand')
server.register_function(isValidCommand, 'isValidCommand')

# start listening  on the given port
server.serve_forever()
