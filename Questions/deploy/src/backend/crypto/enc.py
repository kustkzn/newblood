from Cryptodome.Util.Padding import pad
from itertools import product
import hashlib

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
        
def spesial_encrypt(question:str, key:str):
    key=pad(key.encode(), 8)
    question=question.encode()
    chipherquestion=frenel(question, key)
    return chipherquestion

