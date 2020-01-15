import os
import logging


def create_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(
        logging.Formatter(
            '[%(name)s:%(filename)s:%(lineno)d] - [%(process)d] - %(asctime)s - %(levelname)s - %(message)s'
        )
    )

    logger.addHandler(stdout_handler)

    return logger


LOGGER = create_logger("TRAFFIC-MONITORING")

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

VIDEO = f"{CURRENT_DIR}/data/videos/test.mp4"

OUTPUT_VIDEO_PATH = f"{CURRENT_DIR}/detected/output.mp4"

LOG_FILES_DIRECTORY = f"{CURRENT_DIR}/data/logs/"

DROI = [(750, 405), (1094, 398), (1569, 1028), (501, 1028)]

COUNTING_LINES = []

DEBUG_WINDOW_SIZE = (858, 480)

CAPTURE_FROM_CAM = False

USE_DROI = False

SHOW_DROI = False

MAX_CONS_DETECTION_FAILS = 2

MAX_CONS_TRACKING_FAILS = 3

DETECTION_INTERVAL = 1

DETECTOR = "yolo"

USE_GPU = True

TRACKER = "kcf"

RECORD = True

NO_UI_DISPLAY = False

ENABLE_CONSOLE_LOGGER = True

ENABLE_FILE_LOGGER = True

ENABLE_LOGSTASH_LOGGER = False

SCALE = 0.00392

NMS_THRESHOLD = 0.4

YOLO_CONFIG = {
    "weights_path": f"{CURRENT_DIR}/data/detectors/yolo/yolov3.weights",
    "config_path": f"{CURRENT_DIR}/data/detectors/yolo/yolov3.cfg",
    "classes_path": f"{CURRENT_DIR}/data/detectors/coco_classes.txt",
    "classes_of_interest": f"{CURRENT_DIR}/data/detectors/coco_classes_of_interest.txt",
    "data_path": f"{CURRENT_DIR}/data/detectors/coco.data",
    "threshold": 0.4
}
