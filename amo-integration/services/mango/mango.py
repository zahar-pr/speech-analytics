from __future__ import annotations
import asyncio
import httpx
from ..interfaces import Telephony
from models.mango import MangoRecord
from mixin import MangoMixin
from mango_extractor import MangoExtractor, logger
from fastapi import HTTPException
from typing import NoReturn


class MangoCallRecord(MangoMixin, Telephony):

    def __init__(self):
        self._mp3 = None
        self._phone_number = None
        super().__init__()

    @property
    def mp3_url(self) -> str:
        if self._mp3 is None:
            self._mp3 = self._get_mp3()
        return self._mp3.url

    async def _get_mp3(self) -> MangoCallRecord | NoReturn:
        '''
        Проверяем все ключи в кэше, если среди них есть нужный нам контакт, то берем самый
        старый звонок, удаляем этот звонок из записи
        :param phone_number:
        :return:
        '''
        phone_numbers: list = await self._client.keys()
        if self._phone_number not in phone_numbers:
            logger.error("ERROR: отсутствие контакта в очереди звонков. Телефония: mango office")
            raise Exception("Данный контакт не имеет записанных звонков")
        else:
            recording_id = await self._client.get(self._phone_number)[0]
            if len(phone_numbers) > 1:
                await self._client.set(self._phone_number, phone_numbers[1:])
            else:
                await self._client.delete(self._phone_number)
        url = f'{self._mango_api_url}/vpbx/queries/recording/post'
        js = {
            "recording id": f"{recording_id}",
            "action": "download"
        }
        super()._set_sign(js)
        body = super()._get_body(js)

        async with httpx.Client() as client:
            response = await client.post(url, body)
            if response.status != 302:
                logger.error(
                    f"ERROR: Ошибка получения данных. Статус код ответа: {response.status_code}. Телефония: mango office")
                raise Exception(f"Ошибка получения данных. Статус код ответа: {response.status_code}")
            else:
                file_url = response.json()['Location']
        return MangoRecord(recording_id, file_url)

    @classmethod
    def _check_signature(cls, request) -> None | NoReturn:
        '''
        Проверка валидности сигнатуры для обработки webhook'а
        :param request:
        :return:
        '''
        super()._set_sign(request.js)
        if super()._sign != request.sign:
            logger.error(
                f"ERROR: Ошибка получения уведомления от mango office. Причина: неверная подпись. Телефония: mango office")
            raise HTTPException(status_code=401, detail="Invalid signature")

    @classmethod
    def _check_call_status(cls, request) -> None | NoReturn:
        '''
        Дополнительная проверка, поскольку нет смысла обрабатывать несостоявщиеся звонки
        :param request:
        :return:
        '''
        if int(request.js['entry_result']) == 0:
            logger.error(
                f"ERROR: Ошибка получения уведомления от mango office. Причина: попытка получения несостоявщегося звонка. Телефония: mango office")
            raise HTTPException(status_code=403, detail="Invalid call status")

    def __call__(self, request) -> MangoCallRecord | NoReturn:
        '''
        Сделал класс вызываемым, поскольку проще инкапсулировать сложну логику
        :param request:
        :return:
        '''
        self._check_signature(request),
        self._check_call_status(request)
        request_data = request.js
        extractor = MangoExtractor(request_data["sip_call_id"])
        phone = extractor()
        self._phone_number = phone

        return self.mp3_url
