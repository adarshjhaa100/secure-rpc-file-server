# This program is to provide functionality of client node
import xmlrpc.client
import json

# Client Details obtained from KDC
clientDetails={}

# Registration of a new File Server at kDC at port 8000
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
    print(sendMessage)
    kdcMessage=json.loads(proxy.registerFileServer(sendMessage))
    
    # Store details to global variable
    global clientDetails
    clientDetails=kdcMessage
    print("saved my details")

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
connectToFS()