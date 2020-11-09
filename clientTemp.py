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
    kdcMessage['Kab']=''

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
# Step 3: send Kab(Ra2), Kb(aliceID,Kab)-->toBob  
def authNSP(choiceFS=0):
    number=8001
    global clientDetails
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{number}/")
    randomChallenge=random.randint(1111,9999) #Ra1
    bobID=clientDetails['serverlist'][choiceFS][0]
    
    # Step1
    f=getFernetObject()
    details=json.dumps({
        "Ra1":randomChallenge,
        "aliceID":clientDetails['id'],
        "bobID":bobID
    })
    returnMessage=proxy.serveAlice(details).encode('utf-8')
    
    # step2: Decrypt message from KDC
    message=json.loads(f.decrypt(returnMessage).decode('utf-8')) 
    # print(message)

    #Check random challenge for authenticity of kdc server
    if(message['Ra1']!=randomChallenge):
        print('KDC server unknown')
        return None
    else:
        print('KDC server legal')

    # Save the Session key
    clientDetails['Kab']=message['Kab']
    fsession=Fernet(message['Kab'])     #Session Encryptor
    
    # Step 3:
    Ra2=random.randint(1111,9999)  #Ra2
    # print(randomChallenge2)
    randomChallenge=fsession.encrypt(str(Ra2).encode('utf-8')).decode('utf-8')
    toBob=message['toBob']
    portFS=8101+choiceFS
    proxy2=xmlrpc.client.ServerProxy(f"http://localhost:{portFS}/")
    messageFS=json.dumps({
      'Ra2': randomChallenge,
      'toBob':toBob 
    })
    # Send message to bob
    fromBob=proxy2.authClientFS(messageFS)
    
    # Step 4
    fromBob=fsession.decrypt(fromBob.encode('utf-8')).decode('utf-8')
    fromBob=json.loads(fromBob) 
    # print(fromBob,Ra2)
    RaBob=fromBob['Ra2']
    
    if(Ra2==RaBob+1):
        print('legal Bob')
    else:
        print('illegal bob')
        return None     

    #Step5 : Send Kab(Rb-1)
    verifyRandom=fromBob['Rb']-1
    verifyRandom=fsession.encrypt(str(verifyRandom).encode('utf-8')).decode('utf-8')  
    ack=proxy2.authRandom(verifyRandom) 
    ack=fsession.decrypt(ack.encode('utf-8')).decode('utf-8')
    print(ack)
    print('Files of the FileServer mounted to client')
    clientDetails['port']=portFS

# Once Client is registered, connect to a registered File Server
# All the ports of FS will start from 8080
def connectToFS():
    portFS=clientDetails['port']
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{portFS}/")
    while(True):
        print(f'file-server-{portFS}-commandline',end='$ ')
        myCommand=input()
        if(myCommand=='end'):
            break
        print(proxy.runCommand(myCommand))


# Print all available servers
def printServers():
    serverList=clientDetails['serverlist']
    for index,val in enumerate(serverList):
        print(index, val[0], val[1])


registerNode()

printServers()  #list of servers
choiceFS=int(input("choose bob"))

authNSP(choiceFS)
print(clientDetails)
# connectToFS()