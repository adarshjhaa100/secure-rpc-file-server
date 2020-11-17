# Registers file servers and User nodes, providing them symmetric keys.  
# Provides session keys for authentication using Needham Schroeder Protocol.


from xmlrpc.server import SimpleXMLRPCServer
import json
import secrets
import pandas as pd
from cryptography.fernet import Fernet
import os
import atexit

print('KDC program')

countFS=0
registerKey=Fernet(b'bPFK7Z6AGpWbeohwh3oiQXsYOgYypdeEEUq5ST0_wrU=') #A fernet key temporarily saved for secure reigstration


# Mthod to clear files
def clearFiles(filename):
    file =open(filename,"r+")
    file.truncate(0)
    file.close()

# Method to be called when exiting
def exithandler():
    print('app exiting')
    clearFiles('kdcFiles/FS_keys.csv')
    clearFiles('kdcFiles/client_keys.csv')
    for i in range(countFS):
        os.popen(f'rm -R folder{i+1}')

# Registering the exit function
atexit.register(exithandler)

# Code to register a file server and User Node
def registerNode(message):
    global countFS
    message=registerKey.decrypt(message.encode('utf-8')).decode('utf-8')
    message=json.loads(message)
    print(message)
    # id:16 bit
    # Key: Fernet key
    if(message['id']==None):
        fsInfo={
            "id":secrets.token_hex(16),
            "key":generate_key(),
            "status":True,
            "serverlist":[],
            "countFS":0
        }
        filename=""
        if(message['isFileServer']):
            filename="kdcFiles/FS_keys.csv"
            countFS+=1
        else:
            filename="kdcFiles/client_keys.csv"

        fsInfo['serverlist']=saveFS(fsInfo,filename,countFS)
        fsInfo['countFS']=countFS

        fsInfo=json.dumps(fsInfo)
        # print(fsInfo)
        fsInfo=registerKey.encrypt(fsInfo.encode('utf-8')).decode('utf-8')
        print("File server saved")
        return fsInfo
    return json.dumps({"id":message.id,"status":False})


# Generating assymetric key which is stored and is private for each node 
def generate_key():
    key = Fernet.generate_key()
    return key.decode('utf-8')


# Store The data of file server and Node to a database 
def saveFS(fsInfo,filename,countFS):
    df = pd.DataFrame({
                        'id': [fsInfo['id']], 
                        'key': [fsInfo['key']],
                        'port': 8100+countFS
                      })
    if(os.path.getsize(filename) == 0):
        df.to_csv(filename,header=True)
    else:
        df.to_csv(filename,mode='a',header=False)
    
    # Return a list of server objects
    servList=[]
    if(os.path.getsize('kdcFiles/FS_keys.csv')>0):
        df=pd.read_csv('kdcFiles/FS_keys.csv')['id']
        ports=pd.read_csv('kdcFiles/FS_keys.csv')['port']
        for index,val in enumerate(df):
            servList.append([val,int(ports[index])])
        return servList
    
    return servList


#Update file list at the clients end
# details: AliceID
def updateFileList(details):
    details=json.loads(details)
    clientID=details['clientID']
    fclient=getFernetObject('kdcFiles/client_keys.csv',clientID)    
    
    servList=[]
    if(os.path.getsize('kdcFiles/FS_keys.csv')>0):
        df=pd.read_csv('kdcFiles/FS_keys.csv')['id']
        ports=pd.read_csv('kdcFiles/FS_keys.csv')['port']
        for index,val in enumerate(df):
            servList.append([val,int(ports[index])])
    
    serverList=json.dumps({
        'serverList':servList
    }).encode('utf-8')

    serverList=fclient.encrypt(serverList).decode('utf-8')

    return serverList
    

# get fernet object
def getFernetObject(filename,ID):
    # print('get fernet')
    df=pd.read_csv(filename)
    key=df[df['id']==ID]['key'].tolist()
    # print(key)
    key=key[0]
    f=Fernet(key.encode('utf-8'))
    return f


# From here on decryt using alice's key
# Step 1 : Alice gives Ra1, aliceID and bobID
# Step 2 :return session key encrypted with alice's key
# Ra1,BobID, Session key Kab, and Kb,kdc(A, Kab)-->encrypted with bob key
def serveAlice(details):
    details=json.loads(details)
    aliceID=details['aliceID']
    bobID=details['bobID']
    randomChallenge=details['Ra1']
    session_key=generate_key()
    # print(details)
    
    fclient=getFernetObject('kdcFiles/client_keys.csv',aliceID)    
    fserver=getFernetObject('kdcFiles/FS_keys.csv',bobID)

    toBob=json.dumps({'aliceID':aliceID,'Kab':session_key})
    toBob=fserver.encrypt(toBob.encode('utf-8')).decode('utf-8')
    
    toAlice=json.dumps({
        'Ra1':randomChallenge,
        'bobID':bobID,
        'Kab':session_key,
        'toBob':toBob
    }).encode('utf-8')

    toAlice=fclient.encrypt(toAlice).decode('utf-8')
    
    # print(toAlice)
    return toAlice
    

port_num=8001
server=SimpleXMLRPCServer(("localhost",port_num))
print(f"KDClistening on {port_num}...")

# Registration of procedures
server.register_function(registerNode,'registerFileServer')
server.register_function(serveAlice,'serveAlice')
server.register_function(updateFileList,'updateFileList')

# Run the server
server.serve_forever()


