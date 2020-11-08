import xmlrpc.client
import json

# File server id

number = 8100
proxy = xmlrpc.client.ServerProxy(f"http://localhost:{number}/")

# Request kdc server to register FS


def registerServer(proxy):
    serverMessage = json.dumps({
        "id": None,
        "key": None,
        "isFileServer": False
    })
    print(serverMessage)

    kdcMessage = json.loads(proxy.registerFileServer(serverMessage))
    saveFsDetails(kdcMessage)

# Store the id and encryption key given


def saveFsDetails(kdcMessage):
    print(kdcMessage)
    print("saved my details")


registerServer(proxy)


number = int(
    input("Enter the port of file server you want to communicate with:"))
proxy = xmlrpc.client.ServerProxy(f"http://localhost:{number}/")


while(True):
    print(f'file-server-{number}-commandline', end='$ ')
    myCommand = input()
    if(myCommand == 'end'):
        break
    # if(proxy.isValidCommand(myCommand)==False):
    #     print('Not a valid command')
    #     continue
    print(proxy.runCommand(myCommand))
