import hashlib
import os
from redis.credentials import UsernamePasswordCredentialProvider
import redis.asyncio as redis
from typing import NoReturn

creds_provider = UsernamePasswordCredentialProvider(os.environ["username"],
                                                    os.environ["password"])
redis_client = redis.Redis(host="localhost", port=6379, credential_provider=creds_provider)

class MangoMixin:
    sha_256_hash = hashlib.new("sha256")  # sha256 является обязательным
    _mango_domain: str = os.environ["MANGO_DOMAIN"]
    _mango_api_url: str = f"https//:{_mango_domain}"
    _vpbx_api_key: str = os.environ["VPBX_API_KEY"]
    _vpbx_api_salt: str = os.environ["VPBX_API_SALT"]
    _client = redis_client

    def _set_sign(self, js: dict) -> NoReturn:
        '''

        :param js: ассоциативный список, содержащий значения полей id,
        session_id, abonent_id
        :return: хэш, вычесляемый по условной формуле sha256(vpbx_api_key + json + vpbx_api_salt)
        '''
        self.sha_256_hash.update(
            str(self._vpbx_api_key + ''.join(str(i) for i in js.values()) + self._vpbx_api_salt).decode()
        )
        self._sign = self.sha_256_hash.hexdigest()

    def _get_body(self, js):
        return {
            'vpbx api key': self._vpbx_api_key,
            'sign': self._sign,
            'json': js}

