from cryptography.fernet import Fernet
import json
import secrets
import random


def generate_key(fileName='secret.key'):
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open(fileName, "wb") as key_file:
        key_file.write(key)


def load_key(fileName='secret.key'):
    """
    Load the previously generated key
    """
    return open(fileName, "rb").read()


def encrypt_message(message, fileName='secret.key'):
    """
    Encrypts a message
    """
    key = load_key(fileName)
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message


def decrypt_message(encrypted_message, fileName='secret.key'):
    """
    Decrypts an encrypted message
    """
    key = load_key(fileName)
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode("utf-8")





# Simulating Needam Schroder Algo
ID_a = "1"
Key_a = generate_key("a.key")
N1 = secrets.token_hex(6)
# print(N1)

ID_b = "2"
Key_b = generate_key("b.key")


# A to KDC
messageA = {
    "ID_A":ID_a,
    "ID_B":ID_b,
    "N1":N1
}
encMsgA = encrypt_message(json.dumps(messageA),"a.key")
messageKDC = encMsgA


# KDC to A
messageKDC = decrypt_message(messageKDC,"a.key")
messageKDC = json.loads(messageKDC)
# print(messageKDC)
generate_key('session.key')
encMsgB = {
    "K_session": load_key('session.key').decode("utf-8"),
    "ID_A": messageKDC["ID_A"],
}
# print(encMsgB)
encMsgB = encrypt_message(json.dumps(encMsgB), 'b.key')
messageKDC = {
    "K_session": load_key('session.key').decode("utf-8"),
    "ID_A": messageKDC["ID_A"],
    "ID_B": messageKDC["ID_B"],
    "N1": messageKDC["N1"],
    "encMsgB": encMsgB.decode("utf-8"),
}
messageKDC = encrypt_message(json.dumps(messageKDC), "a.key")
messageA = messageKDC


# A to B
messageA = decrypt_message(messageA,'a.key')
messageA = json.loads(messageA)
sessionKeyA = messageA['K_session']
messageB = messageA['encMsgB'].encode('utf-8')
# print(messageA)


# B to A
messageB = decrypt_message(messageB,'b.key')
messageB = json.loads(messageB)
sessionKeyB = messageB['K_session']
N2 = random.randint(2**1,2**128)
encMsgB = {
    "K_session": sessionKeyB,
    "N2":N2
}
encMsgB = encrypt_message(json.dumps(encMsgB),'session.key')
messageA = encMsgB


# A to B
messageA = decrypt_message(messageA,'session.key')
messageA = json.loads(messageA)
messageA['N2']+=1
messageB = encrypt_message(json.dumps(messageA),'session.key')


# Check if connection established or not
messageB = decrypt_message(messageB,'session.key')
messageB = json.loads(messageB)
if(N2+1==messageB['N2']):
    print("Connection Successfull")
else:
    print('Dobara kr pagal insan')

