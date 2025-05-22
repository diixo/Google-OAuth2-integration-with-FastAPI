import logging
import logging as logger
import time
from dotenv import load_dotenv

from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apis import authentication


logging.basicConfig(
    level=logging.INFO,  # Set the default logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


load_dotenv(override=True)

config = Config(".env")
API_PORT = config.get("API_PORT", default="3400")

allowed_origins = [
    f"http://localhost:{API_PORT}",
    f"http://127.0.0.1:{API_PORT}",
    "null",
    "chrome-extension://<YOUR_EXTENSION_ID>",
]


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify by allowed_origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add Session middleware
app.add_middleware(SessionMiddleware, secret_key=config("SECRET_KEY"))

app.include_router(authentication.router, tags=["Authentication"])


# Logging time taken for each api request
@app.middleware("http")
async def log_response_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.url.path} completed in {process_time:.4f} seconds")
    return response 


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(API_PORT))
