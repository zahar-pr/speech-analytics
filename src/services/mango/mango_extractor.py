from mixin import MangoMixin, use_logging
import httpx

@use_logging('mango')
class MangoExtractor(MangoMixin):

    def __init__(self, recording_id: str):
        super().__init__()
        self.recording_id = recording_id
        pass

    def _extract_record_id(self):
        url = f"{self._mango_api_url}/vpbx/cc/call"
        js = {
            "entry_id": self.recording_id
        }

        super()._set_sign(js)

        body = super()._get_body(js)

        response = httpx.post(url, data=body)
        if response.json()['result'] != 1000:
            self._logger.error("ERROR: некорректный запрос на извлечение идентификатора звонка. Телефония: mango office")
            raise Exception("Некорректный запрос")
        contact_id = response.json()['contact_id']
        return contact_id

    def _extract_phone(self, contact_id: str):
        url = f"{self._mango_api_url}/vpbx/ab/contact"

        js = {
            'contact_id': contact_id,
            'contacnt_ext_fields': True,  # тут без теста не понять, если смысл ставить False
        }

        super()._set_sign(js)

        body = super()._get_body(js)
        response = httpx.post(url, data=body).json()
        if response.get('phone', False):
            return response['phone']
        else:
            self._logger.error("ERROR: некорректный запрос на извлечение номера абонента. Телефония: mango office")
            raise Exception("Ошибка запроса")

    def _save_record_to_redis(self, phone):
        self._client.set(phone, self.recording_id)  # нужно определиться с единым форматом телефонов
        # и предусмотреть подгон под нужный формат

    def __call__(self):
        contact_id = self._extract_record_id()
        phone = self._extract_phone(contact_id)
        return phone
