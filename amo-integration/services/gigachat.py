import base64
import json
import os
import uuid

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

from models.gigachat import GigachatToken, GigachatAnswer
from utils.setup_logger import logger

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)

gigachat_session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 502, 503, 504])
gigachat_session.mount('https://', HTTPAdapter(max_retries=retries))

pem_path = os.path.join(os.path.dirname(__file__), '../conf/russian.pem')
prompt_path = os.path.join(os.path.dirname(__file__), '../conf/prompt.txt')


class GigachatClient:
    def __init__(self):
        self._id = os.environ.get("G_ID")
        self._secret = os.environ.get("GIGACHAT_CLIENT_SECRET")
        self._credentials = f"{self._id}:{self._secret}"
        self._base = base64.b64encode(self._credentials.encode('utf-8')).decode('utf-8')
        self._uuid = str(uuid.uuid4())
        self._token = self._get_token()

    @property
    def token(self) -> str:
        if self._token is None:
            self._token = self._get_token()
        return self._token

    def get_recommendation(self, message: str):
        return self._get_answer(message)
    

    def _get_token(self) -> str:
        gigachat_oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        payload = {
            'scope': os.environ['GIGACHAT_SCOPE'],  # для бизнеса GIGACHAT_API_CORP
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': self._uuid,
            'Authorization': f'Basic {self._base}',
        }
        response = gigachat_session.post(gigachat_oauth_url,
                                         headers=headers,
                                         data=payload,
                                         verify=pem_path)
        if response.status_code != 200:
            logger.error(f"Ошибка получения данных. Статус код ответа: {response.status_code}")
            raise Exception
        token = GigachatToken(
            access_token=response.json()['access_token'],
            expires_at=response.json()['expires_at']
        )
        logger.info(f"Токен Gigachat создан.")
        self._token = token.access_token
        return self._token

    def _get_answer(self, message: str) -> str:
        """
        Получение ответа на промпт
        :param message: расшифрованный звонок
        :return: ответ гигачата на промпт
        """
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        with open(prompt_path, "r") as prompt_file:
            prompt = prompt_file.read()
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Message: {message}")
            payload = json.dumps({
                "model": "GigaChat-Pro",
                "messages": [
                    {
                        "role": "user",
                        "content": f"ПРОМПТ: {prompt} \n СООБЩЕНИЕ: {message}"
                    }
                ],
                "temperature": 1,
                "top_p": 0.1,
                "n": 1,
                "repetition_penalty": 1,
                "update_interval": 0
            })
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self._token}'
            }
            response = gigachat_session.request("POST",
                                                url,
                                                headers=headers,
                                                data=payload,
                                                verify=pem_path)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        print(response.json())
        answer = GigachatAnswer(
            role=response.json()['choices'][0]['message']['role'],
            content=response.json()['choices'][0]['message']['content']
        )
        message = answer.content
        return message
