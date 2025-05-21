import logging
from datetime import datetime, timedelta
from db_utils.db import log_db_user_access


logging.basicConfig(
    level=logging.INFO,  # Set the default logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


DB_PATH = "datastorage/access-test.db"


if __name__ == "__main__":
    print(64*"=")

    first_logged_in = datetime.utcnow() - timedelta(hours=1)

    log_db_user_access("2080", "airis@example.com", "Airis", first_logged_in, datetime.utcnow(), "token-2080-1170", DB_PATH)
    log_db_user_access("1600", "jenny@example.com", "Jenny", first_logged_in, datetime.utcnow(), "token-1600-0900", DB_PATH)
    log_db_user_access("1920", "johny@example.com", "Johny", first_logged_in, datetime.utcnow(), "token-1920-1080", DB_PATH)
    log_db_user_access("1280", "teddy@example.com", "Teddy", first_logged_in, datetime.utcnow(), "token-1280-0720", DB_PATH)

    log_db_user_access("2080", "airis@example.com", "Airis", first_logged_in, datetime.utcnow(), None, DB_PATH)
    log_db_user_access("1600", "jenny@example.com", "Jenny", first_logged_in, datetime.utcnow(), None, DB_PATH)
    log_db_user_access("1920", "johny@example.com", "Johny", first_logged_in, datetime.utcnow(), None, DB_PATH)
    log_db_user_access("1280", "teddy@example.com", "Teddy", first_logged_in, datetime.utcnow(), None, DB_PATH)
