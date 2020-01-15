from detectors.yolo import get_bounding_boxes as gbb


def get_bounding_boxes(frame):
    return gbb(frame)
