from cryptography.fernet import Fernet

key=Fernet.generate_key()
print(key)

f=open('registrationKey.txt','w')
f.write(key.decode('utf-8'))
f.close()
