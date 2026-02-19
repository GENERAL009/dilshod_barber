import requests

ESKIZ_BASE = "https://notify.eskiz.uz"
LOGIN = "/api/auth/login"
SEND  = "/api/message/sms/send"

# ✅ Hammasi shu faylda (env yo'q)
ESKIZ_EMAIL  = "shohrux_malikov@mail.ru"
ESKIZ_SECRET = "BFIHVXcTKmStpoINU7jgf3II4OWMwHEXZhB5GnKb"  # secret key (kabinetdan)
ESKIZ_FROM   = "4546"                      # string bo‘lsin
CALLBACK_URL = ""                          # ixtiyoriy

class EskizClient:
    def __init__(self):
        self.email = ESKIZ_EMAIL
        self.password = ESKIZ_SECRET
        self.sender_from = str(ESKIZ_FROM)   # ✅ string
        self.callback_url = CALLBACK_URL
        self.token = None
        self.session = requests.Session()

    def _login(self):
        r = self.session.post(
            ESKIZ_BASE + LOGIN,
            files={"email": (None, self.email), "password": (None, self.password)},
            timeout=20,
        )

        # ✅ login xatosini ham ko‘rsatamiz
        if r.status_code >= 400:
            raise RuntimeError(f"LOGIN ERROR {r.status_code}: {r.text}")

        self.token = r.json()["data"]["token"]
        return self.token

    def _auth(self):
        if not self.token:
            self._login()
        return {"Authorization": f"Bearer {self.token}"}

    def send_sms(self, phone: str, message: str) -> str:
        payload = {
            "mobile_phone": (None, str(phone)),
            "message": (None, str(message)),
            "from": (None, self.sender_from),
        }
        if self.callback_url:
            payload["callback_url"] = (None, self.callback_url)

        r = self.session.post(
            ESKIZ_BASE + SEND,
            headers=self._auth(),
            files=payload,     # Swagger: multipart/form-data :contentReference[oaicite:2]{index=2}
            timeout=20,
        )

        # ✅ 401 bo'lsa tokenni yangilab ko'ramiz
        if r.status_code == 401:
            self.token = None
            r = self.session.post(
                ESKIZ_BASE + SEND,
                headers=self._auth(),
                files=payload,
                timeout=20,
            )

        # ✅ mana shu joy eng keraklisi: 400 body’ni chiqaradi
        if r.status_code >= 400:
            raise RuntimeError(f"SEND ERROR {r.status_code}: {r.text}")

        return r.json().get("id", "")
