from xmlrpc.server import SimpleXMLRPCServer
import os,sys

# Point out to the folder of server
file_server = input("Enter name of file server folder:")
os.chdir(file_server)

# Check for valid command
def isValidCommand(command:str):
    a=max(  command.find('ls'),
            command.find('pwd'),
            command.find('cp'),
            command.find('cat'),
            command.find('close'))
    if(a==-1):
        return False
    return True

# Run the user command
def runCommand(command):
    if(isValidCommand(command)):
        if(command.find('pwd')!=-1):
            return f'/{file_server}'
        return os.popen(command).read()
    else:
        return f"Command '{command}' not found"


port_num=int(input("Enter the port number"))
server=SimpleXMLRPCServer(("localhost",port_num))
print(f"listening on {port_num}...")

# Register function
server.register_function(runCommand,'runCommand')
server.register_function(isValidCommand,'isValidCommand')

# start listening  on the given port 
server.serve_forever()
