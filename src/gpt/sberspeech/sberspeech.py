import os
import time
import uuid

import requests
from dotenv import load_dotenv

from requests.adapters import HTTPAdapter, Retry

from models import SpeechToken, SpeechFile, SpeechTask, SpeechStatus
from src.utils.logger import use_logging

dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=dotenv_path)

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount(prefix="https://", adapter=HTTPAdapter(max_retries=retries))

sber_rest_endpoint = "https://smartspeech.sber.ru/rest/v1/"
sber_oauth_endpoint = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

pem_path = os.path.join(os.path.dirname(__file__), "../conf/russian.pem")


class SberSpeechClient:
    def __init__(self, file_path: str):
        self._auth_code = os.environ["SBER_AUTH_CODE"]
        self._uuid = str(uuid.uuid4())
        self._token = self._get_token()
        self._file_path = file_path
        self._file = self._upload_file()
        self._task_id = self._create_task_on_recognition()
        self._result_id = self._get_result_id()

    def get_recognition(self):
        return self._get_recognition_data()

    def _get_token(self) -> str:
        url = f"{sber_oauth_endpoint}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "RqUID": self._uuid,
            "Authorization": f"Basic {self._auth_code}",
        }
        body = {
            "scope": os.environ["SBER_SCOPE"],  # для бизнеса SALUTE_SPEECH_CORP
        }
        response = session.post(
            url,
            headers=headers,
            data=body,
            verify=pem_path,
            timeout=10,
        )
        if response.status_code == 200:
            access_token = SpeechToken(
                access_token=response.json()["access_token"],
                expires_at=response.json()["expires_at"],
            )
            return access_token.access_token
        else:
            self._logger.error(
                f"Ошибка получения токена авторизации. Ошибка: {response.status_code}"
            )
            raise Exception(
                f"Ошибка получения токена авторизации. Ошибка: {response.json()}"
            )

    def _upload_file(self):
        """
        Загрузка файла для распознавания
        :return: идентификатор загруженного файла
        """
        url = f"{sber_rest_endpoint}data:upload"
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        response = session.get(self._file_path, stream=True)
        if response.status_code == 200:
            file = response.content
            upload_response = session.post(
                url, headers=headers, data=file, verify=pem_path
            )
            if upload_response.status_code == 200:
                self._logger.info("Файл загружен.")
                uploaded_file = SpeechFile(
                    id=upload_response.json()["result"]["request_file_id"]
                )
                uploaded_file_id = uploaded_file.id
                return uploaded_file_id
            else:
                self._logger.error("Ошибка загрузки файла:", upload_response.text)
                raise Exception("Ошибка загрузки файла:", upload_response.text)

    def _create_task_on_recognition(self):
        """
        Создание задачи на распознавание
        :return: идентификатор созданной задачи
        """
        url = f"{sber_rest_endpoint}speech:async_recognize"
        params = {
            "request_file_id": self._file,
            "options": {
                "language": "ru-RU",
                "audio_encoding": "MP3",
                "hypotheses_count": 1,
                "no_speech_timeout": "20s",
            },
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        response = session.post(url, headers=headers, json=params, verify=pem_path)
        print(response.content)
        if response.status_code == 200:
            task = SpeechTask(id=response.json()["result"]["id"])
            task_id = task.id
            return task_id
        else:
            self._logger.error(
                f"Ошибка получения данных. Статус код ответа: {response.status_code}"
            )
            raise Exception(
                f"Ошибка получения данных. Статус код ответа: {response.json()}"
            )

    def _get_result_id(self):
        """
        Получение идентификатора результата распознавания
        :return: идентификатор результата распознавания
        """
        url = f"{sber_rest_endpoint}task:get"
        params = {
            "id": self._task_id,
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        while True:
            response = session.get(url, headers=headers, params=params, verify=pem_path)
            if response.json()["status"] == 200:
                status = SpeechStatus(
                    status=response.json()["status"],
                    file_id=None,
                    result_status=response.json()["result"]["status"],
                    error=response.json()["result"].get("error", None),
                )
                time.sleep(10)
                if status.result_status == "ERROR":
                    self._logger.error(
                        f"Ошибка распознавания. Статус код ответа: {response.json()['result']['status']}"
                    )
                    raise Exception(
                        f"Ошибка распознавания. Статус код ответа: {response.json()['result']['status']}"
                    )
                elif status.result_status == "DONE":
                    self._logger.info("Распознавание завершено.")
                    status.file_id = response.json()["result"]["response_file_id"]
                    return status.file_id
            else:
                self._logger.error(
                    f"Ошибка получения данных. Статус код ответа: {response.json()['status']}"
                )
                raise Exception(
                    f"Ошибка получения данных. Статус код ответа: {response.json()['status']}"
                )

    def _get_recognition_data(self):
        """
        Получение данных распознавания
        :return: данные распознавания
        """
        url = f"{sber_rest_endpoint}data:download?response_file_id={self._result_id}"
        data = {
            "response_file_id": self._result_id,
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        response = session.get(url, headers=headers, data=data, verify=pem_path)
        if response.status_code == 200:
            result_list = response.json()
            text = b""
            for result in result_list:
                for chunk in result["results"]:
                    text += bytes(chunk["text"], "utf-8")
                    text += b"\n"
            utf8_text = text.decode("utf-8") if isinstance(text, bytes) else text
            return utf8_text
        else:
            self._logger.error(
                f"Ошибка получения данных. Статус код ответа: {response.json()['status']}"
            )
