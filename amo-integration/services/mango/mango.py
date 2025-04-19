import httpx
from amo-integration.models.mango import MangoRecord
from mixin import MangoMixin
from mango_extractor import MangoExtractor
from fastapi import HTTPException
# в проде поменять хост!!!

class MangoCallRecord(MangoMixin):

    def __init__(self, phone_number):
        self._sign = None
        self._mp3_url = None
        self._phone_number = phone_number
        super().__init__()
    async def _get_mp3(self, phone_number):
        '''
        Проверяем все ключи в кэше, если среди них есть нужный нам контакт, то берем самый
        старый звонок, удаляем этот звонок из записи
        :param phone_number:
        :return:
        '''
        phone_numbers: list = await self._client.keys()
        if phone_number not in phone_numbers:
            raise Exception(f"Данный контакт не имеет записанных звонков")
        else:
            recording_id = await self._client.get(phone_number)[0]
            if len(phone_numbers) > 1:
                await self._client.set(phone_number, phone_number[1:])
            else:
                await self._client.delete(phone_number)
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
                raise Exception(f"Ошибка получения данных. Статус код ответа: {response.status_code}")
            else:
                file_url = response.json()['Location']
        return MangoRecord(recording_id, file_url)

    @classmethod
    async def _check_signature(cls, request):
        super()._set_sign(request.js)
        if super()._sign != request.sign:
            raise HTTPException(status_code=401, detail="Invalid signature")

    async def __call__(self, request):
        await self._check_signature(request)
        request = request.js
        extractor = MangoExtractor(request["entry_id"])
        phone = extractor()
        return await self._get_mp3(phone)