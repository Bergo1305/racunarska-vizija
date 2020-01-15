import time
import cv2
import json

from util.image import take_screenshot
from util.logger import get_logger
from util.debugger import mouse_callback
from VehicleCounter import VehicleCounter
from util.logger import init_logger
from config import VIDEO, \
                   CAPTURE_FROM_CAM, \
                   USE_DROI, \
                   SHOW_DROI, \
                   MAX_CONS_DETECTION_FAILS, \
                   MAX_CONS_TRACKING_FAILS, \
                   DETECTION_INTERVAL, \
                   DETECTOR, \
                   TRACKER,\
                   RECORD, \
                   NO_UI_DISPLAY, \
                   DEBUG_WINDOW_SIZE, \
                   DROI, \
                   COUNTING_LINES, \
                   CURRENT_DIR


REF_POINTS = []
LATTER = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
INDEX = 0


def selectpoints (event, x, y, flags, param):
    global refPt
    global videocntrl

    cv2.imshow('SelectPoints', firstFrame)

    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]

    elif event == cv2.EVENT_LBUTTONUP:
        cv2.circle(firstFrame, (x, y), 3, (0, 255, 255), -1)
        cv2.imshow("SelectPoints", firstFrame)
        REF_POINTS.append(refPt)

    elif event == cv2.EVENT_RBUTTONDOWN:
        videocntrl = True


if __name__ == "__main__":

    init_logger()
    logger = get_logger()

    cap = cv2.VideoCapture(VIDEO)
    _, firstFrame = cap.read()
    cv2.namedWindow('SelectPoints', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('SelectPoints', selectpoints)
    cv2.waitKey(0)
    cv2.destroyWindow('SelectPointsq')
    for i in range(0, len(REF_POINTS) - 1, 2):
        COUNTING_LINES.append(
            {
                "label": LATTER[INDEX],
                "line": [
                    REF_POINTS[i][0],
                    REF_POINTS[i + 1][0]
                ]
            }
        )
        INDEX = INDEX + 1

    cap = cv2.VideoCapture(VIDEO)
    if not cap.isOpened():
        raise Exception(f"Invalid video source {VIDEO}")

    ret, frame = cap.read()
    f_height, f_width, _ = frame.shape
    DROI_ = [(0, 0), (f_width, 0), (f_width, f_height), (0, f_height)] if not USE_DROI else DROI

    vehicle_counter = VehicleCounter(
                                        frame,
                                        DETECTOR,
                                        TRACKER,
                                        DROI_,
                                        SHOW_DROI,
                                        int(MAX_CONS_DETECTION_FAILS),
                                        int(MAX_CONS_TRACKING_FAILS),
                                        DETECTION_INTERVAL,
                                        COUNTING_LINES
                                     )
    if RECORD:
        output_video = cv2.VideoWriter(
                                        f"{CURRENT_DIR}/detected/a.mp4",
                                        cv2.VideoWriter_fourcc(*'MJPG'),
                                        30,
                                        (f_width, f_height)
                                      )

    logger.info('Processing started.',
                extra={
                    'meta': {
                            'label': 'START_PROCESS',
                            'counter_config': {
                                'di': DETECTION_INTERVAL,
                                'mcdf': MAX_CONS_DETECTION_FAILS,
                                'mctf': MAX_CONS_TRACKING_FAILS,
                                'detector': DETECTOR,
                                'tracker': TRACKER,
                                'use_droi': USE_DROI,
                                'droi': DROI_,
                                'show_droi': SHOW_DROI,
                                'counting_lines': COUNTING_LINES
                            },
                      },
                      }
                )

    if not NO_UI_DISPLAY:
        cv2.namedWindow('DEBUG', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('DEBUG', mouse_callback, {'frame_width': f_width, 'frame_height': f_height})

    is_paused = False
    output_frame = None
    json_counts = None
    while CAPTURE_FROM_CAM or cap.get(cv2.CAP_PROP_POS_FRAMES) + 1 < cap.get(cv2.CAP_PROP_FRAME_COUNT):
        k = cv2.waitKey(1) & 0xFF
        if k == ord('p'):
            is_paused = False if is_paused else True
            logger.info('Loop paused/played.', extra={'meta': {'label': 'PAUSE_PLAY_LOOP', 'is_paused': is_paused}})
        if k == ord('s') and output_frame is not None:
            take_screenshot(output_frame)
        if k == ord('q'):
            with open(f"{CURRENT_DIR}/counts.json", 'w') as outfile:
                json.dump(json_counts, outfile)
            logger.info('Loop stopped.', extra={'meta': {'label': 'STOP_LOOP'}})
            break

        if is_paused:
            time.sleep(0.5)
            continue

        _timer = cv2.getTickCount()

        if ret:
            vehicle_counter.count(frame)
            json_counts = vehicle_counter.get_counts()
            output_frame = vehicle_counter.visualize()

            if RECORD:
                output_video.write(output_frame)

            if not NO_UI_DISPLAY:
                debug_window_size = DEBUG_WINDOW_SIZE
                resized_frame = cv2.resize(output_frame, debug_window_size)
                cv2.imshow('DEBUG', resized_frame)

        processing_frame_rate = round(cv2.getTickFrequency() / (cv2.getTickCount() - _timer), 2)
        frames_processed = round(cap.get(cv2.CAP_PROP_POS_FRAMES))
        frames_count = round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.debug(
                     'Frame processed.',
                     extra={
                             'meta':  {
                                    'label': 'FRAME_PROCESS',
                                    'frames_processed': frames_processed,
                                    'frame_rate': processing_frame_rate,
                                    'frames_left': frames_count - frames_processed,
                                    'percentage_processed': round((frames_processed / frames_count) * 100, 2),
                                },
                            }
                    )

        ret, frame = cap.read()

    cap.release()
    if not NO_UI_DISPLAY:
        cv2.destroyAllWindows()
    if RECORD:
        output_video.release()
    logger.info('Processing ended.', extra={'meta': {'label': 'END_PROCESS'}})
