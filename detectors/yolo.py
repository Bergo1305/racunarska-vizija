import cv2
import json
import numpy as np
from config import YOLO_CONFIG, USE_GPU, SCALE, NMS_THRESHOLD

YOLO_CONFIG = json.loads(json.dumps(YOLO_CONFIG))

YOLO_CLASSES_PATH = YOLO_CONFIG["classes_path"]
YOLO_CLASSES_OF_INTEREST_PATH = YOLO_CONFIG["classes_of_interest"]
YOLO_CONFIG_PATH = YOLO_CONFIG["config_path"]
YOLO_WEIGHTS_PATH = YOLO_CONFIG["weights_path"]
YOLO_DATA_PATH = YOLO_CONFIG["data_path"]
CONG_THRESHOLD = YOLO_CONFIG["threshold"]

with open(YOLO_CLASSES_PATH,  'r') as classes_file:
    CLASSES = dict(enumerate([line.strip() for line in classes_file.readlines()]))
with open(YOLO_CLASSES_OF_INTEREST_PATH, 'r') as coi_file:
    CLASSES_OF_INTEREST = tuple([line.strip() for line in coi_file.readlines()])

if USE_GPU:
    from pydarknet import Detector
    net = Detector(bytes(YOLO_CONFIG_PATH, encoding='utf-8'),
                   bytes(YOLO_WEIGHTS_PATH, encoding='utf-8'),
                   0,
                   bytes(YOLO_DATA_PATH, encoding='utf-8'))
else:
    net = cv2.dnn.readNet(YOLO_WEIGHTS_PATH, YOLO_CONFIG_PATH)


def get_bounding_boxes_cpu(image):
    image_blob = cv2.dnn.blobFromImage(image, SCALE, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(image_blob)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(output_layers)

    _classes = []
    _confidences = []
    _boxes = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > CONG_THRESHOLD and CLASSES[class_id] in CLASSES_OF_INTEREST:
                width = image.shape[1]
                height = image.shape[0]
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = center_x - w / 2
                y = center_y - h / 2
                _classes.append(CLASSES[class_id])
                _confidences.append(float(confidence))
                _boxes.append([x, y, w, h])

    indices = cv2.dnn.NMSBoxes(_boxes, _confidences, CONG_THRESHOLD, NMS_THRESHOLD)

    _bounding_boxes = []
    for i in indices:
        i = i[0]
        _bounding_boxes.append(_boxes[i])

    return _bounding_boxes, _classes, _confidences


def get_bounding_boxes_gpu(img):
    from pydarknet import Image

    img_darknet = Image(img)
    results = net.detect(img_darknet)

    _bounding_boxes, _classes, _confidences = [], [], []
    for cat, score, bounds in results:
        _class = str(cat.decode('utf-8'))
        if score > CONG_THRESHOLD and _class in CLASSES_OF_INTEREST:
            _bounding_boxes.append(bounds)
            _classes.append(_class)
            _confidences.append(score)

    return _bounding_boxes, _classes, _confidences


def get_bounding_boxes(image):
    if USE_GPU:
        return get_bounding_boxes_gpu(image)
    else:
        return get_bounding_boxes_cpu(image)
