import cv2
from util.blob import Blob
from util.bounding_box import get_overlap, get_box_image
from util.vehicle_info import generate_vehicle_id
from util.logger import get_logger


logger = get_logger()


def _kcf_create(bounding_box, frame):
    tracker = cv2.TrackerKCF_create()
    tracker.init(frame, tuple(bounding_box))
    return tracker


def get_tracker(algorithm, bounding_box, frame):
    if algorithm == 'kcf':
        return _kcf_create(bounding_box, frame)

    raise Exception('Invalid tracking algorithm specified (options:kcf)')


def _remove_stray_blobs(blobs, matched_blob_ids, mcdf):
    for blob_id, blob in list(blobs.items()):
        if blob_id not in matched_blob_ids:
            blob.num_consecutive_detection_failures += 1
        if blob.num_consecutive_detection_failures > mcdf:
            del blobs[blob_id]
    return blobs


def add_new_blobs(boxes, classes, confidences, blobs, frame, tracker, mcdf):
    matched_blob_ids = []
    for i, box in enumerate(boxes):
        _type = classes[i] if classes is not None else None
        _confidence = confidences[i] if confidences is not None else None
        _tracker = get_tracker(tracker, box, frame)

        match_found = False
        for _id, blob in blobs.items():
            if get_overlap(box, blob.bounding_box) >= 0.6:
                match_found = True
                if _id not in matched_blob_ids:
                    blob.num_consecutive_detection_failures = 0
                    matched_blob_ids.append(_id)
                blob.update(box, _type, _confidence, _tracker)

                logger.debug('Blob updated.', extra={
                    'meta': {
                        'label': 'BLOB_UPDATE',
                        'vehicle_id': _id,
                        'bounding_box': blob.bounding_box,
                        'type': blob.type,
                        'type_confidence': blob.type_confidence,
                    },
                })
                break

        if not match_found:
            _blob = Blob(box, _type, _confidence, _tracker)
            blob_id = generate_vehicle_id()
            blobs[blob_id] = _blob
            logger.debug('Blob created.', extra={
                'meta': {
                    'label': 'BLOB_CREATE',
                    'vehicle_id': blob_id,
                    'bounding_box': _blob.bounding_box,
                    'type': _blob.type,
                    'type_confidence': _blob.type_confidence,
                },
            })

    blobs = _remove_stray_blobs(blobs, matched_blob_ids, mcdf)
    return blobs


def remove_duplicates(blobs):
    for blob_id, blob_a in list(blobs.items()):
        for _, blob_b in list(blobs.items()):
            if blob_a == blob_b:
                break

            if get_overlap(blob_a.bounding_box, blob_b.bounding_box) >= 0.6 and blob_id in blobs:
                del blobs[blob_id]
    return blobs


def update_blob_tracker(blob, blob_id, frame):
    success, box = blob.tracker.update(frame)
    if success:
        blob.num_consecutive_tracking_failures = 0
        blob.update(box)
        logger.debug('Vehicle tracker updated.', extra={
            'meta': {
                'label': 'TRACKER_UPDATE',
                'vehicle_id': blob_id,
                'bounding_box': blob.bounding_box,
                'centroid': blob.centroid,
            },
        })
    else:
        blob.num_consecutive_tracking_failures += 1

    return blob_id, blob
