# Google-OAuth-Integration-with-FastAPI

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
```
`pip install "python-jose[cryptography]"`


## HowTo:

**Run api.py**


### Environments `.env`:

`.env` file looks like:
```bash
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
SECRET_KEY = "web-app-secret-key"
REDIRECT_URL = "http://127.0.0.1:3400/auth"
FRONTEND_URL = "http://127.0.0.1:3400/auth"
JWT_SECRET_KEY = <your-jwt-secret-key>
```


## Google Authentication OAuth2:

* `Регистрируем в Google Cloud Console расширение как WebApplication, получаем CLIENT_ID` и т.д. (SECRET_KEY...) = downloaded json

* Вы на клиенте (расширение или сайт) открываете страницу авторизации Google.

* Google спрашивает разрешение и отдаёт авторизационный код.

* Вы отправляете этот код на ваш сервер.

* Сервер обменивает код на access_token и id_token (в котором есть email, имя и т.п.).

* Сервер сохраняет JWT (или сессию) и кладёт в cookie (token).

* Возвращать токен, creds в RedirectResponse на адрес, в наше случае полученный от chrome.identity.getRedirectURL("provider_cb") прокинутый через сессию (либо на welcome-страницу либо на redirect_url с токеном)


## References:

* https://blog.futuresmart.ai/integrating-google-authentication-with-fastapi-a-step-by-step-guide + [Full Code in our GitHub](https://github.com/PradipNichite/FutureSmart-AI-Blog/tree/main/Google%20OAuth%20Integration%20with%20FastAPI)
