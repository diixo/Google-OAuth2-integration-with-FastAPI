# Google-OAuth2-integration-with-FastAPI

Backend for [chrome-ext](https://github.com/diixo/chrome-ext)


## Requirements:

```bash
python-dotenv
mysql-connector-python
requests
fastapi
uvicorn
python-jose[cryptography]
authlib
pyjwt
itsdangerous
google-auth
pydantic
sqlalchemy
```

Dependency on httpx>=0.23:
```bash
pip install httpx==0.27.2
```

### Environments:

Create `.env` that looks like:
```bash
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
SECRET_KEY = "web-app-secret-key"
REDIRECT_URL = "http://127.0.0.1:3400/auth"
FRONTEND_URL = "http://127.0.0.1:3400/auth"
JWT_SECRET_KEY = <your-jwt-secret-key>
```


## Google Authentication OAuth2:

* `Регистрируем в Google Cloud Console расширение как WebApplication, получаем CLIENT_ID` (or download as json)

* Вы на клиенте (расширение или сайт) открываете страницу авторизации Google.

* Google спрашивает разрешение и отдаёт авторизационный код.

* Вы отправляете этот код на ваш сервер.

* Сервер обменивает код на access_token и id_token (в котором есть email, имя и т.п.).

* Сервер сохраняет JWT (или сессию) в БД, и кладёт в cookie (token).

* Возвращать токен, creds в RedirectResponse на адрес, в наше случае полученный от **chrome.identity.getRedirectURL("provider_cb")** прокинутый через сессию (либо возврат на welcome-страницу, либо на Google redirect_url с токеном)


## References:

* [integrating-google-authentication-with-fastapi-a-step-by-step-guide](https://blog.futuresmart.ai/integrating-google-authentication-with-fastapi-a-step-by-step-guide) + [Full Code in our GitHub](https://github.com/PradipNichite/FutureSmart-AI-Blog/tree/main/Google%20OAuth%20Integration%20with%20FastAPI)


## Examples:

* https://medium.com/@vivekpemawat/enabling-googleauth-for-fast-api-1c39415075ea
* https://parlak-deniss.medium.com/fastapi-authentication-with-google-oauth-2-0-9bb93b784eee
* https://blog.hanchon.live/guides/google-login-with-fastapi/
