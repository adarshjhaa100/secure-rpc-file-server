# from cryptography.fernet import Fernet

# key=Fernet.generate_key()
# print(key)

# f=open('registrationKey.txt','w')
# f.write(key.decode('utf-8'))
# f.close()
from subprocess import Popen

proc=Popen('cat registrationKey.txt'.split())
# print(proc.)

f=open('registrationKey.txt','r+')
result={}
s=''
for line in f:
    s+=line

result['res']=s
# print(result['res'])
