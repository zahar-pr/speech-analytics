from typing import NoReturn

from dotenv import load_dotenv
import os
import httpx
from src.crm.interfaces import CRM

from src.utils.logger import use_logging
dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=dotenv_path)

@use_logging(log_file='bitrix24')
class Bitrix24Lead(CRM):

    def __init__(self, lead_id: int) -> NoReturn:
        self._token = os.environ["BITRIX24_TOKEN"]
        self._api_url = os.environ["BITRIX24_URL"]
        self._lead_id = lead_id
        self._contact_id = None
        self._contact_phone = None

    def _get_lead_main_contact_id(self) -> None:
        '''
        Получаю информацию по сделке.
        Устанавливаю атрибуты класса, такие как номер телефона и айди контакта
        :return:
        '''
        get_lead_url = self._api_url + self._token + f'/crm.lead.get/'
        request_data = {'ID': {self._lead_id}}
        response = httpx.post(get_lead_url, data=request_data)
        response_dict = response.json()['result']
        if response.status_code == 200 and response_dict.get('error', True):
            self._contact_id = response_dict['PHONE']['ID']
            self._contacts_phone = [i['PHONE']['VALUE'] for i in response_dict]
            self._logger.info('ID контакта поулчен.CRM: Bitrix24')
            self._logger.info('Номер телефона контакта получен.CRM: Bitrix24')
        else:
            self._logger.error(
                f"Ошибка запроса. Статус код: {response.status_code}. Описание: {response_dict.get('error', '')} .CRM: Bitrix24")
            raise Exception("Unvalid request to Bitrix24")

    @property
    def contacts_phone(self):
        return self._contact_phone

    def post_note(self, note: str) -> None:
        post_note_url = self._api_url + self._token + f'/crm.timeline.comment.add/'
        request_data = {'fields': {
            'ENTITY_ID': self._lead_id,
            'ENTITY_TYPE': 'lead',
            'COMMENT': "Рекомендации" + note
        }}
        response = httpx.post(post_note_url, data=request_data)
        response_dict = response.json()
        if response_dict.get('error', None):
            self._logger.error(f"Ошибка создания заметки.Ошибка: {response_dict.get('error_description')}.Статуск код ошибки: {response.status_code}.CRM: Bitrix24")
            raise Exception("Bitrix24 post note request error")
        else:
            self._logger.info(f"Заметка создана. ID заметки:{response_dict['result']}.CRM: Bitrix24")