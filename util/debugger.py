import os
import ast
import cv2

from config import DEBUG_WINDOW_SIZE
from .logger import get_logger


logger = get_logger()


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        capture_pixel_position(x, y, param['frame_width'], param['frame_height'])


def capture_pixel_position(window_x, window_y, frame_w, frame_h):
    debug_window_size = DEBUG_WINDOW_SIZE
    x = round((frame_w / debug_window_size[0]) * window_x)
    y = round((frame_h / debug_window_size[1]) * window_y)
    logger.info('Pixel position captured.', extra={'meta': {'label': 'PIXEL_POSITION', 'position': (x, y)}})
