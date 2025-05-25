# Google-OAuth2-integration-with-FastAPI

Backend for [chrome-ext](https://github.com/diixo/chrome-ext)


## Requirements:

```bash
authlib
fastapi
google-auth
itsdangerous
pyjwt
python-jose[cryptography]
python-dotenv
requests
sqlalchemy
uvicorn
```

Dependency on httpx>=0.23:
```bash
pip install httpx==0.27.2
pip install pydantic==1.10.22
```

Check:
```bash
pip install sqlalchemy==2.0.24
pip install fastapi==0.103.2
```

Check:
```bash
pip install pydantic==1.10.22
```


### Environments:

Create `.env` that looks like:
```bash
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
SECRET_KEY = "web-app-secret-key"
REDIRECT_URL = "http://127.0.0.1:8001/auth"
FRONTEND_URL = "http://127.0.0.1:8001/auth"
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


## Routing of Working process

#### 1. Генерируем JWT-токен при авторизации
В момент успешной авторизации, например через Google OAuth:

* создаём **JWT-токен с помощью jwt.encode(...)**

* отдаём его клиенту через Response


#### 2. Запросы на fastAPI
Когда браузерное расширение делает запросы к серверу (например, **fetch('/save-selection')**), скрипт автоматически прикрепляет к этим запросам token, используя `headers`

* Извлекается клиентом (расширением) локально сохранённый токен, полученный от сервера

* Предварительно проверяется `expiresAt` перед отправкой
```javascript
method: 'POST',
headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${stored.token}`,
}
```


#### 3. Проверка и валидация запросов

* Сервер валидирует токен

Пример на fastAPI эндпоинте:
```python
@app.post("/save-selection")
async def save_selection(data: SelectionData, current_user: dict = Depends(get_current_user)):
```

* берёт token из `headers` запроса - с помощью get_current_user_header (get_current_user версия для куки)

* декодирует его через **jwt.decode(...)**

* извлекает **user_id**, **email** и т.д.

* если всё ок — передаёт эти данные в эндпоинт


## References:

* [integrating-google-authentication-with-fastapi-a-step-by-step-guide](https://blog.futuresmart.ai/integrating-google-authentication-with-fastapi-a-step-by-step-guide) + [Full Code in GitHub](https://github.com/PradipNichite/FutureSmart-AI-Blog/tree/main/Google%20OAuth%20Integration%20with%20FastAPI)


## Examples:

* https://medium.com/@vivekpemawat/enabling-googleauth-for-fast-api-1c39415075ea
* https://parlak-deniss.medium.com/fastapi-authentication-with-google-oauth-2-0-9bb93b784eee
* https://blog.hanchon.live/guides/google-login-with-fastapi/
