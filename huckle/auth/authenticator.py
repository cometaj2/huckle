from requests.auth import AuthBase
import base64


class HCOAKBearerAuth(AuthBase):
    def __init__(self, keyid, apikey):
        self.keyid = keyid
        self.apikey = apikey
        self.auth_string = f"{keyid}:{apikey}"

    def __call__(self, r):
        encoded = base64.b64encode(self.auth_string.encode()).decode()
        r.headers["authorization"] = f"Bearer {encoded}"
        return r
