# This program is to provide functionality of FileServer node
from os import error
import random
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import os
import json
import time
from cryptography.fernet import Fernet

# Initialize the file server by selecting the directory
file_server = ''
# Variable to store registration 
serverDetails={}
port_num=8100
Kab=''#Session encryptor
registerKey=Fernet(b'bPFK7Z6AGpWbeohwh3oiQXsYOgYypdeEEUq5ST0_wrU=') #A fernet key temporarily saved for secure reigstration


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
    sendMessage=registerKey.encrypt(sendMessage.encode('utf-8')).decode('utf-8')
    kdcMessage=proxy.registerFileServer(sendMessage)
    
    kdcMessage=registerKey.decrypt(kdcMessage.encode('utf-8')).decode('utf-8')
    kdcMessage=json.loads(kdcMessage)
    # print(kdcMessage)


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
            command.find('cat'),)

    if(a==-1):
        return False
    return True

# Run the user command
def runCommand(command):
    command=Kab.decrypt(command.encode('utf-8')).decode('utf-8')
    
    if(isValidCommand(command)):
        if(command.find('pwd')!=-1):
            return f'/{file_server}'
        
        obj=os.popen(command)
        returnVal=obj.read()
        return returnVal
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
# Step 3, 4 
Rb=0  #Random Challenge
def authClientFS(message):
    message=json.loads(message)
    # print(message)
    key=serverDetails['key']
    f=Fernet(key)
    toBob=f.decrypt(message['toBob'].encode('utf-8')).decode('utf-8')
    toBob=json.loads(toBob)
    
    f2=Fernet(toBob['Kab']) #Session Encryptor
    global Kab
    Kab=f2
    
    Ra2=message['Ra2']
    Ra2=int(f2.decrypt(Ra2.encode('utf-8')).decode('utf-8'))
    print(toBob,Ra2)
    
    # Step4: send Ra2-1 and Rb encrypted with Kab
    global Rb
    Rb=random.randint(1111,9999)
    toAlice=json.dumps({
        "Ra2":Ra2-1,
        "Rb":Rb
    }).encode('utf-8')

    toAlice=f2.encrypt(toAlice).decode('utf-8')
    return toAlice
    
#Step 5: Authenticate client's random challenge
def authRandom(message):
    message=Kab.decrypt(message.encode('utf-8')).decode('utf-8')
    print(message)
    if(int(message)+1==Rb):
        return Kab.encrypt('Acknowleged'.encode('utf-8')).decode('utf-8')
    raise 'Error'

# Authenticate client using needham schroeder
# 3. get Kab(Ra2), Kb(aliceID,Kab)-->toBob
# 4. send Kab(Ra2-1,Rb)
# 5. get Kab(Rb-1)
def authServeClient():
    global port_num
    server=SimpleXMLRPCServer(("localhost",port_num))
    print(f"listening for auth {port_num}...")
    
    # start listening  on the given port 
    server.register_function(authClientFS,'authClientFS')
    server.register_function(authRandom,'authRandom')
    server.register_function(runCommand,'runCommand')
    server.serve_forever()
    

registerFS()
print(serverDetails)
os.chdir(file_server)
print(os.popen('pwd').read())

authServeClient()

# serveClient()

