import xmlrpc.client

# File server id

number=input('Enter Port of File Server')

proxy=xmlrpc.client.ServerProxy(f"http://localhost:{number}/")


while(True):
    print(f'file-server-{number}-commandline',end='$ ')
    myCommand=input()
    if(myCommand=='end'):
        break
    # if(proxy.isValidCommand(myCommand)==False):
    #     print('Not a valid command')
    #     continue
    print(proxy.runCommand(myCommand))