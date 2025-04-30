import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi_restful.cbv import cbv
from src.crm.amo.amo import AmoLead, amo_session
from src.gpt.gigachat.gigachat import GigachatClient, gigachat_session
from src.services.pbx.pbx import pbx_session
from src.gpt.sberspeech.sberspeech import SberSpeechClient, session
from utils.setup_self._logger import self._logger
from models import MangoRequest
from src.services.mango.mango import MangoCallRecord

def events_controller(form_data, fl):
    self._logger.info(form_data)
    receiving_lead(form_data, fl)


def receiving_lead(form_data, fl):
    lead_id = int(form_data.get('leads[add][0][id]'))
    self._logger.info(f'Создана сделка lead_id: {lead_id}')
    if fl == 'a':
        lead = AmoLead(lead_id)
    receiving_contact_phone(lead)


def receiving_contact_phone(crm_lead, telephony):
    contact_phone = crm_lead.contacts_phone

    if not contact_phone:
        return {"status_code": 500}

    self._logger.info(f'Телефон из сделки: {contact_phone}')
    result = receiving_record_file(contact_phone, telephony)
    set_crm_data(crm_lead, result)


def receiving_record_file(phone, telephony_class):
    telephony = telephony_class(phone_number=phone)
    record_file_url = telephony()

    self._logger.info(f'Ссылка на запись разговора: {record_file_url}')

    return processing_sber_speech(record_file_url)


def processing_sber_speech(file_url: str):
    sber_speech = SberSpeechClient(file_url)
    transcribed_text = sber_speech.get_recognition()

    self._logger.info(f'Распознанный текст: {transcribed_text}')

    return get_gigachat_recommendation(transcribed_text)


def get_gigachat_recommendation(text: str):
    gigachat = GigachatClient()
    gigachat_recommendation = gigachat.get_recommendation(text)

    self._logger.info(f'Рекомендация Gigachat: {gigachat_recommendation}')

    return gigachat_recommendation


def set_crm_data(lead, gigachat_recommendation: str) -> None:
    '''
    интерфейс гарантирует наличие метода post_note у всех интегрированных crm
    :param lead: CRM subclass
    :param gigachat_recommendation: str
    :return: None
    '''
    lead.post_note(gigachat_recommendation)