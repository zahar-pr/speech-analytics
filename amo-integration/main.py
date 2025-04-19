import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException

from services.amo import AmoLead, amo_session
from services.gigachat import GigachatClient, gigachat_session
from services.pbx import PbxCallRecord, pbx_session
from services.sberspeech import SberSpeechClient, session
from utils.setup_logger import logger
from models.mango import MangoRequest
from mango.mango import MangoCallRecord
app = FastAPI()

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)


@app.post("/receive_webhook/")
async def receive_webhook(request: Request):
    """
    Получение события создания новой сделки по webhook от АмоСРМ
    :param request:
    :return:
    """
    form_data = await request.form()

    events_contoller(form_data)

    return closing_session()

@app.post('/mango_webhook/')
async def mango_webhook(request: MangoRequest):
    MangoRequest.check_signature(request)
    call_record = MangoCallRecord()
    await call_record()

@app.exception_handler(HTTPException)
async def http_exception_handler(exc: HTTPException):
    return {"status_code": exc.status_code}


@app.exception_handler(Exception)
async def server_error():
    return {"status_code": 500}


async def events_contoller(form_data):
    logger.info(form_data)
    await receiving_lead(form_data)


async def receiving_lead(form_data):
    lead_id = int(form_data.get('leads[add][0][id]'))
    logger.info(f'Создана сделка lead_id: {lead_id}')

    await receiving_contact_phone(lead_id)


async def receiving_contact_phone(id):
    amo_lead = AmoLead(lead_id = id)
    contact_phone = await amo_lead.get_contact_phone()

    if not contact_phone:
        return {"status_code": 500}
    
    logger.info(f'Телефон из сделки: {contact_phone}')

    result = await receiving_record_file(contact_phone)

    await set_amo_data(amo_lead, result)
    
    
async def receiving_record_file(phone):
    pbx = PbxCallRecord(phone_number = phone)
    record_file_url = await pbx.mp3_url

    logger.info(f'Ссылка на запись разговора: {record_file_url}')

    return await processing_sber_speech(record_file_url)


async def processing_sber_speech(file_url):
    sber_speech = SberSpeechClient(file_url)
    transcribed_text = await sber_speech.get_recognition()

    logger.info(f'Распознанный текст: {transcribed_text}')

    return get_gigaChat_recommendation(transcribed_text)


async def get_gigaChat_recommendation(text):
    gigachat = GigachatClient()
    gigachat_recommendation = await gigachat.get_recommendation(text)

    logger.info(f'Рекомендация Gigachat: {gigachat_recommendation}')

    return await gigachat_recommendation


async def set_amo_data(amo_lead, gigachat_recommendation):
    await amo_lead.post_note_to_amo(gigachat_recommendation)


def closing_session():
    gigachat_session.close()
    pbx_session.close()
    amo_session.close()
    session.close()

    return {"status_code": 200}
