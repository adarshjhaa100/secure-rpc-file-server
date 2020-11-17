# A user nodes allows a user to securely access files on various remote servers using mutual authentication through a command line interface(CLI). 
import xmlrpc.client
import json
from cryptography.fernet import Fernet
import random
# Client Details obtained from KDC
clientDetails={}
registerKey=Fernet(b'bPFK7Z6AGpWbeohwh3oiQXsYOgYypdeEEUq5ST0_wrU=') #A fernet key temporarily saved for secure reigstration

# Class to add colored text to console
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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

    sendMessage=registerKey.encrypt(sendMessage.encode('utf-8')).decode('utf-8')
    kdcMessage=proxy.registerFileServer(sendMessage)
    kdcMessage=registerKey.decrypt(kdcMessage.encode('utf-8')).decode('utf-8')
    kdcMessage=json.loads(kdcMessage)
    
    kdcMessage['Kab']=''

    # Store details to global variable
    global clientDetails
    clientDetails=kdcMessage
    print("saved my details")

def getFernetObject():
    f=Fernet(clientDetails['key'].encode('utf-8'))
    return f

# Get updated list of file servers
def getUpdatedList():
    number=8001
    global clientDetails
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{number}/")
    details=json.dumps({
        'clientID':clientDetails['id']
    })
    message=proxy.updateFileList(details)
    key=getFernetObject()
    message=key.decrypt(message.encode('utf-8')).decode('utf-8')
    message=json.loads(message)
    clientDetails['serverlist']=message['serverList']

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
        print('KDC server illegal')
        return None
    else:
        pass

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
        # print('legal Bob')
        pass
    else:
        print('illegal bob')
        return None     

    #Step5 : Send Kab(Rb-1)
    verifyRandom=fromBob['Rb']-1
    verifyRandom=fsession.encrypt(str(verifyRandom).encode('utf-8')).decode('utf-8')  
    ack=proxy2.authRandom(verifyRandom) 
    ack=fsession.decrypt(ack.encode('utf-8')).decode('utf-8')
    # print(ack)
    print(f'Files of the FileServer {choiceFS} mounted to client')
    clientDetails['port']=portFS

#Function to execute help command in console
def helpCommand():
    print()
    print("These are the list of available commands:")
    print('ls    - list files in current directory')
    print('pwd   - list present working directory')
    print("cp a b- copy file from 'a' to 'b' ")
    print("cat f - list contents of file 'f' ")
    print('end   - end the session')
    print('fs-list - list file servers')
    print('cd fileserverID - change directory to the mentioned fileServer')
    print()

# Once Client is registered, connect to a registered File Server
# All the ports of FS will start from 8080
def connectToFS():
    portFS=clientDetails['port']
    fsession=Fernet(clientDetails['Kab'])
    proxy=xmlrpc.client.ServerProxy(f"http://localhost:{portFS}/")
    while(True):
        getUpdatedList()
        print(f'{bcolors.OKCYAN}{bcolors.BOLD}file-server-{portFS}-commandline{bcolors.ENDC}',end='$ ')
        myCommand=input()
        getUpdatedList()
        # In case user wnats to end session
        if(myCommand=='end'):
            break

        #help
        if(myCommand.find('help')>-1):
            helpCommand()
            continue    

        # get a list of file servers
        if(myCommand.find('fs-list')>-1):
            printServers()
            continue

        # In case user wants to change directory
        if(myCommand.find('cd')>-1 and len(myCommand.split())>1 ):
            connectAndAuth(myCommand.split()[1])
            break

        myCommand=fsession.encrypt(myCommand.encode('utf-8')).decode('utf-8')
        result=proxy.runCommand(myCommand)
        result=fsession.decrypt(result.encode('utf-8')).decode('utf-8')
        result=json.loads(result)
        print(result['val'])

# Print all available servers
def printServers():
    serverList=clientDetails['serverlist']
    print()
    print('sl', 'fsname', '  port')
    for index,val in enumerate(serverList):
        print(index,f' folder{val[1]-8100}',f' {val[1]}' )


# authorize and Connect to a give fileServer
def connectAndAuth(choiceFS):
    authNSP(int(choiceFS))
    # print(clientDetails)
    connectToFS()


registerNode()

printServers()  #list of servers
choiceFS=int(input("choose File Server to connect to: "))

connectAndAuth(choiceFS)

