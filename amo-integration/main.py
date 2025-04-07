import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException

from services.amo import AmoLead, amo_session
from services.gigachat import GigachatClient, gigachat_session
from services.pbx import PbxCallRecord, pbx_session
from services.sberspeech import SberSpeechClient, session
from utils.setup_logger import logger

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
    logger.info(form_data)
    lead_id = int(form_data.get('leads[add][0][id]'))
    logger.info('Создана сделка lead_id: %s', lead_id)
    amo_lead = AmoLead(lead_id=lead_id)
    contact_phone = amo_lead.get_contact_phone()
    if not contact_phone:
        return {"status_code": 500}
    logger.info('Телефон из сделки: %s', contact_phone)
    pbx = PbxCallRecord(phone_number=contact_phone)
    record_file_url = pbx.mp3_url
    logger.info('Ссылка на запись разговора: %s', record_file_url)
    sber_speech = SberSpeechClient(record_file_url)
    transcribed_text = sber_speech.get_recognition()
    logger.info('Распознанный текст: %s', transcribed_text)
    gigachat = GigachatClient()
    gigachat_recommendation = gigachat.get_recommendation(transcribed_text)
    logger.info('Рекомендация Gigachat: %s', gigachat_recommendation)
    amo_lead.post_note_to_amo(gigachat_recommendation)
    gigachat_session.close()
    pbx_session.close()
    amo_session.close()
    session.close()
    return {"status_code": 200}


@app.exception_handler(HTTPException)
async def http_exception_handler(exc: HTTPException):
    return {"status_code": exc.status_code}


@app.exception_handler(Exception)
async def server_error():
    return {"status_code": 500}
