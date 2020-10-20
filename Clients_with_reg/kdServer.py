from xmlrpc.server import SimpleXMLRPCServer
import json
import secrets
import pandas as pd
from cryptography.fernet import Fernet
import os


print('KDC program')

# Code to register a file server
def registerFS(message,fileName):
    message=json.loads(message)
    print(message['id'])
    
    # id:16 bit
    # Key: Fernet key
    if(message['id']==None):
        fsInfo={
            "id":secrets.token_hex(16),
            "key":generate_key(),
            "status":True,
        }
        saveFS(fsInfo,fileName)
        return json.dumps(fsInfo)
    return json.dumps({"id":message.id,"status":False})

# Generating assymetric key which is stored and is private for each node 
def generate_key():
    key = Fernet.generate_key()
    print(key)
    return key.decode('utf-8')

# Store The data of file server to a database 
def saveFS(fsInfo,filename):
    print(fsInfo)
    # input_df = pd.read_csv(filename)
    # print("hello input df",input_df)
    df = pd.DataFrame({
                        'id': [fsInfo['id']], 
                        'key': [fsInfo['key']]
                      }, index=[fsInfo['id']])
    if(os.path.getsize(filename) == 0):
        df.to_csv(filename,header=True)
    else:
        df.to_csv(filename,mode='a',header=False)
    print("File server saved")

# Read File
def readFiles(filename):
    df=pd.read_csv(filename)
    print(df[df['id']=='952717ae1263a0cb2b68a6046b691d32'])

# readFiles()

port_num=8001
server=SimpleXMLRPCServer(("localhost",port_num))
print(f"KDClistening on {port_num}...")

# Registration of procedures
server.register_function(registerFS,'registerFileServer')

# Run the server
server.serve_forever()


