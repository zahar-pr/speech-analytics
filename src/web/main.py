import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi_restful.cbv import cbv
from src.crm.amo.amo import AmoLead, amo_session
from src.gpt.gigachat.gigachat import GigachatClient, gigachat_session
from src.services.pbx.pbx import pbx_session
from src.gpt.sberspeech.sberspeech import SberSpeechClient, session
from src.utils.logger import use_logging
from models import MangoRequest
from src.services.mango.mango import MangoCallRecord

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



def closing_session():
    gigachat_session.close()
    pbx_session.close()
    amo_session.close()
    session.close()

    return {"status_code": 200}

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000, reload=True, log_level='info', workers=5, timeout_graceful_shutdown=30)