# File for adding new functionalities to the fS
import xmlrpc.client
import json
# File server id


# Registration of File Server
# number=input('Enter Port of KDC')
number=8000
proxy=xmlrpc.client.ServerProxy(f"http://localhost:{number}/")

# Request kdc server to register FS
def registerServer(proxy):
    serverMessage=json.dumps({
        "id":None,
        "key":None,
        "isFileServer":False
    })
    print(serverMessage)

    kdcMessage=json.loads(proxy.registerFileServer(serverMessage))
    saveFsDetails(kdcMessage)

# Store the id and encryption key given
def saveFsDetails(kdcMessage):
    print(kdcMessage)
    print("saved my details")

registerServer(proxy)