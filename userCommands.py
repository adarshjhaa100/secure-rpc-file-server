import os
number=8000
# os.system library for executing shell commands

def runCommand(command):
    return os.popen(command).read()

def isValidCommand(command:str):
    a=max(  command.find('ls'),
            command.find('pwd'),
            command.find('cp'),
            command.find('cat'))
    if(a==-1):
        return False
    return True

while(True):
    print(f'file-server-{number}-commandline',end='$ ')
    myCommand=input()
    if(myCommand=='end'):
        break
    if(isValidCommand(myCommand)==False):
        print('Not a valid command')
        continue
    print(runCommand(command=myCommand))
