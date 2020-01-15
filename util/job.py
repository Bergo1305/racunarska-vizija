import os
import uuid
import time


def get_job_id():
    if os.getenv('JOB_ID') is None:
        os.environ['JOB_ID'] = 'job_' + str(int(time.time())) + '_' + uuid.uuid4().hex
    return os.getenv('JOB_ID')
