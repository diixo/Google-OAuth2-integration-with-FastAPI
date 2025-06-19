import logging
import logging as logger
import time
from dotenv import load_dotenv
from typing import List
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from server import authentication_api
from server.authentication_api import get_current_user_header
from server.extension_utils import Db_json, ContentItemModel
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.INFO,  # Set the default logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

load_dotenv(override=True)

db_json = Db_json()

config = Config("server/.env")
API_PORT = config.get("API_PORT", default="8001")

allowed_origins = [
    f"http://localhost:{API_PORT}",
    f"http://127.0.0.1:{API_PORT}",
    f"https://viix.co",
    "chrome-extension://liefnpejhcabdhpfapmmngaabjioelja",
]


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # or specify by allowed_origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add Session middleware
app.add_middleware(SessionMiddleware, secret_key=config("SECRET_KEY"))

app.include_router(authentication_api.router, tags=["Authentication"])


# Logging time taken for each api request
@app.middleware("http")
async def log_response_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.url.path} completed in {process_time:.4f} seconds")
    return response



class SelectionData(BaseModel):
    url: str
    selection_html: str


@app.post("/save-selection")
async def save_selection(data: SelectionData, current_user: dict = Depends(get_current_user_header)):
    global db_json

    user_email = current_user.get("user_email")

    logger.info(f"E-mail: {user_email}, Received URL: {data.url}")
    #print(f"Received Selection HTML:\n{data.selection_html}")

    soup = BeautifulSoup(data.selection_html, 'html.parser')

    all_text = soup.get_text(strip=False)

    #print("all_text:", all_text)

    all_items = all_text.split('\n')

    all_items = [ item.strip() for item in all_items if item.strip() != "" ]

    if len(all_items) > 1:
        summary = " ".join(all_items)
        all_items.append(summary)

    db_json.save_new_item(user_email, data.url, all_items)

    #print(f"Extracted Text:\n{all_text}")

    return {
        "status": "ok",
        "all_text": all_items[-1],
        "items_count": "items:" + str(len(all_items)),
    }


class HtmlPage(BaseModel):
    url: str
    tag_name: str
    html: str


@app.post("/parse-save-page")
async def parse_save_page(data: HtmlPage, current_user: dict = Depends(get_current_user_header)):
    global db_json

    url = data.url.strip('/')
    print(f"Received URL: {url}")

    soup = BeautifulSoup(data.html, "html.parser")

    tag_name = ["h1"] if data.tag_name == "" else data.tag_name

    item_list = [item.get_text(strip=True) for item in soup.find_all(tag_name)]
    logger.info(f"item_list.sz={len(item_list)}")
    logger.info(item_list)

    db_json.save_new_item(current_user.get("user_email"), url, item_list)

    return {
        "status": "ok",
        "received_url": url,
        "items_count": "items:" + str(len(item_list)),
    }



class StatusResponse(BaseModel):
    status: int

@app.post("/add-bookmark-page", response_model=StatusResponse)
async def add_bookmark_page(data: HtmlPage, current_user: dict = Depends(get_current_user_header)):
    global db_json

    logger.info(f"Received URL: {data.url}")
    logger.info(f"Received user-text: {data.tag_name}")
    logger.info(f"Received title-description: {data.html}")
    description = data.tag_name if data.tag_name else data.html
    logger.info(f"Resulted description: {description}")

    result = db_json.save_new_bookmark(current_user.get("user_email"), data.url, description)
    if result is not None:
        return JSONResponse(status_code=500, content={"details": f"Bookmark already exists:\n{result}"})
    return JSONResponse(status_code=200, content={"details": "Bookmark added successfully"})


class SelectionTags(BaseModel):
    url: str
    tag_prompt: str
    selection_html: str


@app.post("/add-selection-tags")
async def add_selection_tags(data: SelectionTags, current_user: dict = Depends(get_current_user_header)):
    logger.info(f"<<-- add-selection-tags")
    return JSONResponse(status_code=200, content={"details": "ok"})


@app.get("/search-ext", response_model=List[str])
async def search_ext(query: str = Query(...), current_user: dict = Depends(get_current_user_header)):
    global db_json

    logger.info(f"email: {current_user.get('user_email')}, query: {query}")

    dataset = db_json.create_dataset_json(current_user.get('user_email'))
    content = dataset["content"]
    return list(content.keys())


@app.post("/bookmarks")
def get_bookmarks(email: str = Body(..., embed=True)):
    global db_json

    logger.info(f"email: {email}")
    dataset = db_json.create_dataset_json(email)

    return JSONResponse(content = {
        "status": "success",
        "bookmarks": dataset.get("bookmarks", dict())
        },
        status_code=200
    )


@app.post("/ai-search", response_model=List[ContentItemModel])
async def ai_search(str_request: str = Body(..., embed=True)):
    global db_json
    return db_json.search(str_request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(API_PORT))

