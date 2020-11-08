# This program is to provide functionality of client node
import xmlrpc.client
import json
from cryptography.fernet import Fernet
import random
# Client Details obtained from KDC
clientDetails={}

# Registration of a new user node at kDC at port 8001
def registerNode():
    # Info of KDC
    number=8001
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{number}/")
    # Make isFileServer false here
    sendMessage=json.dumps({
        "id":None,
        "key":None,
        "isFileServer":False
    })
    kdcMessage=json.loads(proxy.registerFileServer(sendMessage))
    
    # Store details to global variable
    global clientDetails
    clientDetails=kdcMessage
    print("saved my details")


def getFernetObject():
    f=Fernet(clientDetails['key'].encode('utf-8'))
    return f


# Needham schroeder
# Step 1 : Alice gives Ra1, aliceID and bobID
# Step 2 :return session key encrypted with alice's key
# Ra1,BobID, Session key Kab, and Kb,kdc(A, Kab)-->encrypted with bob key
def authNSP():
    number=8001
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{number}/")
    randomChallenge=random.randint(1111,9999)
    
    # Step1
    f=getFernetObject()
    details=json.dumps({
        "Ra1":randomChallenge,
        "aliceID":clientDetails['id'],
        "bobID":"bobID"
    })
    returnMessage=proxy.serveAlice(details).encode('utf-8')
    # step2
    message=json.loads(f.decrypt(returnMessage).decode('utf-8'))
    print(message)



# Once Client is registered, connect to a registered File Server
# All the ports of FS will start from 8080
def connectToFS():
    portFS=input('Enter Port of File Server')
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{portFS}/")
    while(True):
        print(f'file-server-{portFS}-commandline',end='$ ')
        myCommand=input()
        if(myCommand=='end'):
            break
        print(proxy.runCommand(myCommand))


registerNode()
print(clientDetails)

# connectToFS()
authNSP()