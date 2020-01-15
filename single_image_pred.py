import cv2
from detectors.detector import get_bounding_boxes
from config import CURRENT_DIR

IMAGE_PATH = f"{CURRENT_DIR}/data/screenshots/ff.jpg"
IMAGE_NAME = IMAGE_PATH.split("/")[-1].split(".")[0]
IMAGE_EXT = IMAGE_PATH.split("/")[-1].split(".")[1]

if __name__ == "__main__":

    image = cv2.imread(IMAGE_PATH)
    _bounding_boxes, _classes, _confidences = get_bounding_boxes(image)
    font = cv2.FONT_HERSHEY_DUPLEX
    line_type = cv2.LINE_8

    for i in range(0, len(_bounding_boxes)):
        (x, y, w, h) = [int(v) for v in _bounding_boxes[i]]
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(image, _classes[i], (x, y - 5), font, 1, (255, 0, 0), 2, line_type)

    # cv2.imwrite(f"{IMAGE_NAME}_detected.{IMAGE_EXT}", image)
    cv2.imshow("fdf", image)
    cv2.waitKey(0)
