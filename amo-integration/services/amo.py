import os
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

from models.amo import AmoContact
from utils.setup_logger import logger
from interfaces import CRM

dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=dotenv_path)

amo_session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
amo_session.mount("https://", HTTPAdapter(max_retries=retries))

amo_domain = os.environ["AMO_DOMAIN"]
amo_api_base_url = f"https://{amo_domain}/api/v4/"


class AmoLead(CRM):
    def __init__(self, lead_id: int):
        self._token = os.environ["AMO_TOKEN"]
        self._domain = os.environ["AMO_DOMAIN"]
        self._lead_id = lead_id
        self._comment_from_id = os.environ["AMO_COMMENT_FROM_ID"]
        self._contact_id = self._get_lead_main_contact_id(lead_id=lead_id)

    @property
    def contacts_phone(self):
        return self._get_first_phone()

    def post_note(self, note: str) -> None:
        return self._post_note(note)

    def _get_lead_main_contact_id(self, lead_id: int) -> int | None:
        """ 
        Получает id контакта, который является основным контактом для созданной сделки
        :param lead_id: идентификатор сделки
        :return: идентификатор главного контакта или None, если контакта нет
        """
        url = f"{amo_api_base_url}leads/{lead_id}/links"
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        response = amo_session.get(url, headers=headers)
        if response.status_code == 200:
            embedded_list = response.json()["_embedded"]["links"]
            contacts_list = [
                AmoContact(
                    contact_id=contact["to_entity_id"],
                    is_main_contact=contact["metadata"]["main_contact"],
                )
                for contact in embedded_list
                if contact["to_entity_type"] == "contacts"
            ]
            main_contact = [
                contact for contact in contacts_list if contact.is_main_contact
            ][0]
            logger.info(f"Основной контакт для сделки найден.CRM: Amo")
            return main_contact.contact_id
        else:
            logger.error(
                f"Не удалось получить основной контакт из сделки. Статус код: {response.status_code}.CRM: Amo"
            )
            raise Exception(
                f"Не удалось получить основной контакт из сделки. Статус код: {response.status_code}.CRM: Amo"
            )

    def _get_first_phone(self):
        url = f"{amo_api_base_url}contacts/{self._contact_id}"
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        response = amo_session.get(url, headers=headers)
        custom_fields_list = response.json()["custom_fields_values"]
        phones_list = [
            phone["values"][0]["value"]
            for phone in custom_fields_list
            if phone["field_code"] == "PHONE"
        ]
        logger.info(f"Телефон получен.CRM: Amo")
        return phones_list

    def _post_note(self, note: str) -> None:
        """
        Отправляет заметку в AMO
        :param note: текст заметки
        :return:
        """
        url = f"{amo_api_base_url}leads/{self._lead_id}/notes"
        headers = {
            "Authorization": f"Bearer {os.environ['AMO_TOKEN']}",
            "Content-Type": "application/json",
        }
        data = [
            {
                "params": {"text": f"Рекомендации: {note}"},
                "created_by": int(self._comment_from_id),
                "note_type": "common",
                "is_need_to_trigger_digital_pipeline": False,
            },
        ]
        response = amo_session.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logger.error(
                f"Не удалось добавить заметку. Статус код ответа: {response.json()}.CRM: Amo"
            )
        else:
            logger.info(f"Заметка добавлена. Статус код ответа: {response.status_code}.CRM: Amo")
