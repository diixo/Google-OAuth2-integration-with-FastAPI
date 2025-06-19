
import json
import logging
import logging as logger
from pathlib import Path
from starlette.config import Config
from server.smart_search import SmartSearch

logging.basicConfig(
    level=logging.INFO,  # Set the default logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


config = Config("server/.env")
REDIRECT_URL = config("REDIRECT_URL")

path_db_index = "server/db-storage/db-index.bin"


class Db_json:

    def __init__(self):
        self.dataset = None
        self.filepath = None
        self.smart_search = None


    def open_dataset(self, filepath):
        if self.dataset is None:
            self.dataset = dict()
            self.filepath = filepath

            if Path(filepath).exists():
                fd = open(filepath, 'r', encoding='utf-8')
                self.dataset = json.load(fd)

                if self.smart_search is None:
                    self.smart_search = SmartSearch()

                # handling bookmarks to smart-search index
                if Path(path_db_index).exists():
                    logger.info("smart_search.open -->>")
                    self.smart_search.open_file(path_db_index)
                    logger.info("smart_search.open <<--")
                else:
                    logger.info("smart-search index >>")
                    bookmarks = self.dataset["bookmarks"]
                    self.smart_search.add_texts_to_index([line.lower() for line in bookmarks.values()])
                    self.smart_search.write_index(path_db_index)
                    logger.info("smart-search index <<")

            if "content" not in self.dataset:
                self.dataset["content"] = dict()
            if "bookmarks" not in self.dataset:
                self.dataset["bookmarks"] = dict()
        return self.dataset


    def create_dataset_json(self, user_email: str):
        import uuid
        import hashlib

        #filepath = hashlib.sha256(user_email.encode('utf-8')).hexdigest()[:32]
        # [0..f] -->> [a..p]
        #filepath = ''.join(chr(ord('a') + int(c, 16)) for c in filepath)

        filepath = "server/db-storage/"

        if REDIRECT_URL.find("http://127.0.0.1") >= 0 or user_email is None:
            filepath = filepath + "debug.json"
            self.open_dataset(filepath)
        else:
            #UUID4 = (8,4,4,4,12)
            secret_bias_namespace = uuid.UUID("22401260-2000-1125-2080-117021601215")
            self.filepath = filepath + str(uuid.uuid5(secret_bias_namespace, user_email)) + ".json"

            logger.info(f"filepath = {filepath}")

            self.dataset = dict()

            if Path(self.filepath).exists():
                fd = open(self.filepath, 'r', encoding='utf-8')
                self.dataset = json.load(fd)

            if "content" not in self.dataset:
                self.dataset["content"] = dict()
            if "bookmarks" not in self.dataset:
                self.dataset["bookmarks"] = dict()
        return self.dataset


    def save_new_item(self, user_email: str, url: str, i_txt: list):
        url = url.strip('/')
        self.create_dataset_json(user_email)

        chapter = self.dataset["content"]

        if url not in chapter:
            chapter[url] = []

        txt = chapter[url]
        txt_set = set(txt)
        for t in i_txt:
            if t not in txt_set: txt.append(t)
        chapter[url] = txt

        with open(self.filepath, 'w', encoding='utf-8') as fd:
            json.dump(self.dataset, fd, ensure_ascii=False, indent=2)


    def save_new_bookmark(self, user_email: str, url: str, description: str):
        url = url.strip('/')
        self.create_dataset_json(user_email)

        chapter = self.dataset["bookmarks"]
        if url in chapter:
            logger.info(f"url: {url}")
            return chapter[url]

        if self.smart_search is not None:
            if self.smart_search.add_str_to_index(description):
                self.smart_search.write_index(path_db_index)
                chapter[url] = description
                with open(self.filepath, 'w', encoding='utf-8') as fd:
                    json.dump(self.dataset, fd, ensure_ascii=False, indent=2)
            else:
                return description
        else:
            chapter[url] = description
            with open(self.filepath, 'w', encoding='utf-8') as fd:
                json.dump(self.dataset, fd, ensure_ascii=False, indent=2)
        return None
