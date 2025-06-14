
import json
import logging as logger
from pathlib import Path
from starlette.config import Config


config = Config("server/.env")
REDIRECT_URL = config("REDIRECT_URL")


def create_dataset_json(user_email: str):
    import uuid
    import hashlib

    #filepath = hashlib.sha256(user_email.encode('utf-8')).hexdigest()[:32]
    # [0..f] -->> [a..p]
    #filepath = ''.join(chr(ord('a') + int(c, 16)) for c in filepath)

    if REDIRECT_URL.find("http://127.0.0.1") >= 0 or user_email is None:
        filepath = "debug"
    else:
        #UUID4 = (8,4,4,4,12)
        secret_bias_namespace = uuid.UUID("22401260-2000-1125-2080-117021601215")
        filepath = str(uuid.uuid5(secret_bias_namespace, user_email))

    filepath = "server/db-storage/" + filepath + ".json"

    logger.info(f"filepath = {filepath}")

    dataset = dict()

    if Path(filepath).exists():
        fd = open(filepath, 'r', encoding='utf-8')
        dataset = json.load(fd)

    if "content" not in dataset:
        dataset["content"] = dict()
    if "bookmarks" not in dataset:
        dataset["bookmarks"] = dict()

    return dataset, filepath


def save_new_item(user_email: str, url: str, i_txt: list):
    url = url.strip('/')
    dataset, filepath = create_dataset_json(user_email)

    chapter = dataset["content"]

    if url not in chapter:
        chapter[url] = []

    txt = chapter[url]
    txt_set = set(txt)
    for t in i_txt:
        if t not in txt_set: txt.append(t)
    chapter[url] = txt

    with open(filepath, 'w', encoding='utf-8') as fd:
        json.dump(dataset, fd, ensure_ascii=False, indent=2)


def save_new_bookmark(user_email: str, url: str, description: str):
    url = url.strip('/')
    dataset, filepath = create_dataset_json(user_email)

    chapter = dataset["bookmarks"]
    if url in chapter:
        logger.info(f"url: {url}")
        return chapter[url]

    chapter[url] = description
    with open(filepath, 'w', encoding='utf-8') as fd:
        json.dump(dataset, fd, ensure_ascii=False, indent=2)
    return None
