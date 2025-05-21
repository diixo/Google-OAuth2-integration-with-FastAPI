from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request, Cookie
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
from fastapi.responses import JSONResponse
from jose import JWTError, jwt, ExpiredSignatureError, JWTError
import traceback
import requests
import os
from dotenv import load_dotenv
from db_utils.db import log_db_user_access
import logging as logger
from fastapi import Depends


DB_PATH = "datastorage/access.db"

load_dotenv(override=True)

router = APIRouter()

# Load configurations
config = Config(".env")

# Setup OAuth2
oauth = OAuth()

oauth.register(
    name="auth_demo",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    authorize_state=config("SECRET_KEY"),
    redirect_uri="http://127.0.0.1:8000/auth",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)


# Secret key used to encode JWT tokens (should be kept secret)
SECRET_KEY = config("JWT_SECRET_KEY")
ALGORITHM = "HS256"
REDIRECT_URL = config("REDIRECT_URL")
FRONTEND_URL = config("FRONTEND_URL")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Cookie(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("sub")
        user_email: str = payload.get("email")

        if user_id is None or user_email is None:
            raise credentials_exception

        return {"user_id": user_id, "user_email": user_email}

    except ExpiredSignatureError:
        # Specifically handle expired tokens
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Please login again.")
    except JWTError:
        # Handle other JWT-related errors
        traceback.print_exc()
        raise credentials_exception
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Not Authenticated")



@router.get("/login")
async def login(request: Request):
    request.session.clear()
    referer = request.headers.get("referer")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    # Получаем redirect_uri от клиента (расширения)
    redirect_uri = request.query_params.get("redirect_uri")
    logger.info(f"redirect_uri:{redirect_uri}")

    if not redirect_uri:
        return {"error": "Missing redirect_uri"}

    redirect_url = os.getenv("REDIRECT_URL")
    # прокидываем redirect_uri через сессию
    request.session["login_redirect"] = redirect_uri

    return await oauth.auth_demo.authorize_redirect(request, redirect_url, prompt="consent")


@router.route("/auth")
async def auth(request: Request):
    state_in_request = request.query_params.get("state")

    logger.info(f"Request Session: {request.session}")
    logger.info(f"Request state (from query params): {state_in_request}")

    try:
        token = await oauth.auth_demo.authorize_access_token(request)
    except Exception as e:
        logger.info(str(e))
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    try:
        user_info_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f'Bearer {token["access_token"]}'}
        google_response = requests.get(user_info_endpoint, headers=headers)
        user_info = google_response.json()
    except Exception as e:
        logger.info(str(e))
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    user = token.get("userinfo")
    expires_in = token.get("expires_in")
    # user_id always the same for the same user within the same project (client_ID) in Google-API
    user_id = user.get("sub")
    iss = user.get("iss")
    user_email = user.get("email")
    first_logged_in = datetime.utcnow()
    last_accessed = datetime.utcnow()

    user_name = user_info.get("name")
    #user_pic = user_info.get("picture")

    if iss not in ["https://accounts.google.com", "accounts.google.com"]:
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Google authentication failed.")

    # Create JWT token
    access_token_expires = timedelta(seconds=expires_in)
    access_token = create_access_token(data={"sub": user_id, "email": user_email}, expires_delta=access_token_expires)

    #log_db_user(user_id, user_email, user_name, first_logged_in, last_accessed)
    #log_db_token(access_token, user_email)

    if log_db_user_access(user_id, user_email, user_name, first_logged_in, last_accessed, None, DB_PATH) == None:
        raise HTTPException(status_code=401, detail="Google authentication failed (wrong user_id).")

    ######################### Return to Welcome-page
    # return RedirectResponse(f"/welcome?name={user_name}&email={user_email}")

    ######################### Extract passed chrome.identity.getRedirectURL and return
    #redirect_uri = request.query_params.get("redirect_uri")
    redirect_uri = request.session.get("login_redirect")

    logger.info(f"User_name: {user_name}")
    logger.info(f"User_email: {user_email}")
    logger.info(f"User_id: {user_id}, redirect_uri: {redirect_uri}")

    final_url = f"{redirect_uri}?token={access_token}&user={user_name}&email={user_email}"
    return RedirectResponse(url=final_url)

    ######################### Return by Google redirect_url
    redirect_url = request.session.pop("login_redirect", "")
    logger.info(f"Redirecting to: {redirect_url}")
    response = RedirectResponse(redirect_url)
    print(f"Access Token: {access_token}")
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=True,        # Ensure you're using HTTPS
        samesite="strict",  # Set the SameSite attribute to None
    )
    return response


@router.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request):
    name = request.query_params.get("name")
    email = request.query_params.get("email")

    return f"""
    <html>
        <head><title>Welcome</title></head>
        <body>
            <h2>Добро пожаловать, {name}!</h2>
            <p>Ваша почта: {email}</p>
        </body>
    </html>
    """


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    response = JSONResponse(content={"message": "Logged out successfully."})
    response.delete_cookie("token")
    return response


@router.get("/aiveex")
async def get_response(current_user: dict = Depends(get_current_user)):
    return {"message": "Welcome!", "user": current_user}
