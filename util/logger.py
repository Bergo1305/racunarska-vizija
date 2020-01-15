import os
import ast
import logging
import pathlib
from pythonjsonlogger import jsonlogger

from util.job import get_job_id
from config import ENABLE_LOGSTASH_LOGGER, ENABLE_FILE_LOGGER, ENABLE_CONSOLE_LOGGER


class MetaFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'meta'):
            record.meta = {}
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['logger'] = record.name
        log_record['level'] = record.levelname


def init_logger():

    job_id = get_job_id()

    logger = logging.getLogger(job_id)
    logger.addFilter(MetaFilter())
    logger.setLevel(logging.DEBUG)

    enable_console_logger = ast.literal_eval(str(ENABLE_CONSOLE_LOGGER))
    if enable_console_logger:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO) # https://docs.python.org/3/library/logging.html#logging-levels
        stream_formatter = logging.Formatter('[%(asctime)-15s] %(levelname)-8s: %(message)s %(meta)s')
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    enable_file_logger = ast.literal_eval(str(ENABLE_FILE_LOGGER))
    if enable_file_logger:
        log_files_directory = os.getenv('LOG_FILES_DIRECTORY')
        print(log_files_directory)
        pathlib.Path(log_files_directory).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(log_files_directory, job_id + '.log')
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = CustomJsonFormatter('(created) (logger) (level) (message)')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    enable_logstash_logger = ast.literal_eval(str(ENABLE_LOGSTASH_LOGGER))
    if enable_logstash_logger:
        pass


def get_logger():
    return logging.getLogger(get_job_id())
