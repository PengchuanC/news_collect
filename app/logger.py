import logging

LOG_PATH = "news_collect.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M"
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
logs = logging.getLogger(__name__)
