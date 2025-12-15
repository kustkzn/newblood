from Crypto.Util.Padding import pad
from itertools import product
import hashlib

def get_key_word(user:str): 
    key='' #TODO
    return key

def func(R:bytes, key:bytes):
    Rnew=b''
    for i in range(8):
        a=bytes([R[i] ^ key[i]])
        a=bytes([hashlib.sha1(a).digest()[i]])
        Rnew+=a
    return Rnew

def frenel(text:bytes, key:bytes):
    if len(text)%16!=0:
        text=pad(text, 16)
    ciphertext=b''
    for i in range(0, len(text), 16):
        L=text[i:i+8]
        R=text[i+8:i+16]
        for j in range(8):
            keyj=key[-j:]+key[:-j]
            R=func(R, keyj)
            L = bytes(lb ^ rb for lb, rb in zip(L, R))
        ciphertext+=L+R
    return ciphertext.hex()
        


def encrypt(question:str, user:str):
    key=(get_key_word(user)).encode()
    question=question.encode()
    chipherquestion=frenel(question, key)
    return chipherquestion.hex()


#Flag format kustkzn{16 символов}

text=b'kustkzn{ass_is_big_as_di}'
key=b'slowDOWN'
print(frenel(text, key))

cipher=frenel(text, key)


def attack(ciphertext):
    cipher=bytes.fromhex(ciphertext)
    spis=list('1234567890_{}asdfghjklzxcvbnmqwertyuiopZXCVBNMASDFGHJKLQWERTYUIOP')
    flag=['']*25
    for i in spis: # восстановим первый блок
        pt=i.encode()*16
        ct=bytes.fromhex(frenel(pt, key))
        for j in range(8, 16):
            if ct[j]==cipher[j] and (bytes([pt[j]^ct[j-8]^cipher[j-8]]))==bytes([b'kustkzn{'[j-8]]):
                flag[j]=flag[j]+i
    for i in range(8):
        flag[i]='kustkzn{'[i]
    # восстановим второй блок 
    pt=b'a'*24+b'}'
    ct=bytes.fromhex(frenel(pt, key))
    for j in range(16, 24):
        flag[j]=bytes([pt[j]^ct[j]^cipher[j]]).decode()
    flag[24]='}'
    return flag
    
flag=attack(cipher)

for p in  product(*[list(s) for s in flag]):
    print(''.join(list(p)))