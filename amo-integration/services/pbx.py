import os
import time

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

from models.pbx import CallRecord
from utils.setup_logger import logger
from interfaces import Telephony
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)

pbx_base_url = 'https://api2.onlinepbx.ru/'

pbx_session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
pbx_session.mount('https://', HTTPAdapter(max_retries=retries))


class PbxCallRecord(Telephony):
    def __init__(self, phone_number: str):
        self._auth_key = os.environ['PBX_AUTH_KEY']
        self._domain = os.environ['PBX_DOMAIN']
        self._token = self._get_access_token()
        self._phone_numbers = phone_number
        self._mp3 = None


    @property
    def mp3_url(self):
        if self._mp3 is None:
            self._mp3 = self._get_mp3()
        return self._mp3.url

    def _get_access_token(self):
        url = f'{pbx_base_url}{self._domain}/auth.json'
        data = {'auth_key': self._auth_key}
        response = pbx_session.post(url, data=data)
        if response.status_code != 200:
            logger.error(f"Ошибка получения данных. Статус код ответа: {response.status_code}")
            raise Exception(f"Ошибка получения данных. Статус код ответа: {response.status_code}")
        else:
            key = response.json()['data']['key']
            key_id = response.json()['data']['key_id']
            logger.info(f"Токен PBX создан.")
            return f"{key_id}:{key}"

    def _get_mp3(self):
        """
        Получение mp3 файла записи звонка по номеру телефона из созднной сделки
        :return: ссылка на mp3 файл
        """
        url = f'{pbx_base_url}{self._domain}/mongo_history/search.json'
        headers = {
            "x-pbx-authentication": self._token,
        }
        params = {
            # "end_stamp_to": int(time.time()),
            "sub_phone_numbers": self._phone_numbers,
            # "end_stamp_to": time.time(),
        }
        uuid_response = pbx_session.post(url, headers=headers, data=params)
        if uuid_response.status_code == 200:
            if not uuid_response.json()['data']:
                logger.error(f"Нет данных. Статус код ответа: {uuid_response.status_code}")
                raise Exception(f"Нет данных. Статус код ответа: {uuid_response.status_code}")
            call_record = CallRecord(uuid=uuid_response.json()['data'][0]['uuid'], url=None)
            url_response = pbx_session.post(url, headers=headers, data={'uuid': call_record.uuid, 'download': 1})
            call_record.url = url_response.json()['data']
            return call_record
        else:
            logger.error(f"ERROR: Ошибка получения данных. Статус код ответа: {uuid_response.status_code}. Телефония: pbx")
            raise Exception(f"Ошибка получения данных. Статус код ответа: {uuid_response.status_code}")

    def __call__(self):
        return self._mp3
