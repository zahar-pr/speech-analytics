import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi_restful.cbv import cbv
from services.amo import AmoLead, amo_session
from services.gigachat import GigachatClient, gigachat_session
from services.pbx import pbx_session
from services.sberspeech import SberSpeechClient, session
from utils.setup_logger import logger
from models.handlers import MangoRequest, TelephonesList
from services.mango.mango import MangoCallRecord
from services.pbx import PbxCallRecord
from services.interfaces import Telephony

app = FastAPI()
app_router = APIRouter(prefix='/api/v1')
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=dotenv_path)


@cbv(app_router)
class Handlers:

    @app_router.post("/receive_webhook/")
    async def receive_webhook(self, request: Request):
        """
        Получение события создания новой сделки по webhook от АмоСРМ
        :param request:
        :return:
        """
        form_data = await request.form()
        events_controller(form_data, fl='b')

        return closing_session()

    @app_router.post('/mango_webhook/')
    async def mango_webhook(self, request: MangoRequest):
        '''
        Получение уведомления о завершении звонка по webhook'у от manngo office
        :param request:
        :return:
        '''
        call_record = MangoCallRecord()
        call_record(request)

   # @app_router.post('/pbx_webhook/')
    #async def pbx_webhook(self, request: Request):
        #call_record = PbxCallRecord()

    #@app_router.post('/set_telephones/')
    #async def set_telephones(self, request: TelephonesList):
        #pass

@app.exception_handler(HTTPException)
async def http_exception_handler(exc: HTTPException):
    return {"status_code": exc.status_code}


@app.exception_handler(Exception)
async def server_error():
    return {"status_code": 500}


def events_controller(form_data, fl):
    logger.info(form_data)
    receiving_lead(form_data, fl)


def receiving_lead(form_data, fl):
    lead_id = int(form_data.get('leads[add][0][id]'))
    logger.info(f'Создана сделка lead_id: {lead_id}')
    if fl == 'a':
        lead = AmoLead(lead_id)
    receiving_contact_phone(lead)


def receiving_contact_phone(crm_lead, telephony):
    contact_phone = crm_lead.contacts_phone

    if not contact_phone:
        return {"status_code": 500}

    logger.info(f'Телефон из сделки: {contact_phone}')
    result = receiving_record_file(contact_phone, telephony)
    set_crm_data(crm_lead, result)


def receiving_record_file(phone, telephony_class):
    telephony = telephony_class(phone_number=phone)
    record_file_url = telephony()

    logger.info(f'Ссылка на запись разговора: {record_file_url}')

    return processing_sber_speech(record_file_url)


def processing_sber_speech(file_url: str):
    sber_speech = SberSpeechClient(file_url)
    transcribed_text = sber_speech.get_recognition()

    logger.info(f'Распознанный текст: {transcribed_text}')

    return get_gigachat_recommendation(transcribed_text)


def get_gigachat_recommendation(text: str):
    gigachat = GigachatClient()
    gigachat_recommendation = gigachat.get_recommendation(text)

    logger.info(f'Рекомендация Gigachat: {gigachat_recommendation}')

    return gigachat_recommendation


def set_crm_data(lead, gigachat_recommendation: str) -> None:
    '''
    интерфейс гарантирует наличие метода post_note у всех интегрированных crm
    :param lead: CRM subclass
    :param gigachat_recommendation: str
    :return: None
    '''
    lead.post_note(gigachat_recommendation)


def closing_session():
    gigachat_session.close()
    pbx_session.close()
    amo_session.close()
    session.close()

    return {"status_code": 200}
