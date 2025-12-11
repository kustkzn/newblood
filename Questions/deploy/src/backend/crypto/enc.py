from Crypto.Util.Padding import pad
import hashlib

def get_key_word(user:str): 
    key='' #TODO
    return key

def func(R:bytes, key:bytes):
    Rnew=b''
    for i in range(8):
        a=bytes([R[i] ^ key[i]])
        a=hashlib.sha1(a).digest()[i]
        Rnew+=a
    return Rnew

def frenel(text:bytes, key:bytes):
    textpadded=pad(text, 16)
    ciphertext=b''
    for i in range(0, len(textpadded), 16):
        L=textpadded[i:i+8]
        R=textpadded[i+8:i+16]
        for j in range(8):
            keyj=key[-j:]+key[:-j]
            R=func(R, keyj)
            L = bytes(lb ^ rb for lb, rb in zip(L, R))
        ciphertext+=L+R
    return ciphertext
        


def encrypt(question:str, user:str):
    key=(get_key_word(user)).encode()
    question=question.encode()
    chipherquestion=frenel(question, key)
    return chipherquestion.hex()

