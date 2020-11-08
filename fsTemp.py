# This program is to provide functionality of FileServer node
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import os
import json
import time

from cryptography import fernet
from cryptography.fernet import Fernet

# Initialize the file server by selecting the directory
file_server = ''
# Variable to store registration 
serverDetails={}
port_num=8100


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
    os.popen(f'mkdir folder{countFS}')
    time.sleep(0.1)
    global file_server,port_num
    file_server=f'folder{countFS}'
    port_num+=countFS

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
def serveClient(port_num):
    server=SimpleXMLRPCServer(("localhost",port_num))
    print(f"listening on {port_num}...")
    
    # Register function
    server.register_function(runCommand,'runCommand')

    # start listening  on the given port 
    server.serve_forever()


# Read client's auth

# Step 3, 4,5 
def decodeClientMessage(message):
    message=json.loads(message)
    # print(message)
    key=serverDetails['key']
    f=Fernet(key)
    toBob=f.decrypt(message['toBob'].encode('utf-8')).decode('utf-8')
    toBob=json.loads(toBob)
    
    f2=Fernet(toBob['Kab']) #Session Encryptor

    Ra2=message['Ra2']
    Ra2=int(f2.decrypt(Ra2.encode('utf-8')).decode('utf-8'))
    
    print(toBob,Ra2)

    return "jkewfwekwfew"
    

# Authenticate client using needham schroeder
# 3. get Kab(Ra2), Kb(aliceID,Kab)-->toBob
# 4. send Kab(Ra2-1,Rb)
# 5. get Kab(Rb-1)
def authClient():
    global port_num
    server=SimpleXMLRPCServer(("localhost",port_num))
    print(f"listening for auth {port_num}...")
    


    # start listening  on the given port 
    server.register_function(decodeClientMessage,'decodeClient')
    server.serve_forever()
    

registerFS()
print(serverDetails)
os.chdir(file_server)
print(os.popen('pwd').read())

authClient()

# serveClient()

