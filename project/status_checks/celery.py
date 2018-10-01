from celery.task.control import inspect
from watchman.decorators import check


@check
def celery_worker_check():
    try:
        insp = inspect()
        d = insp.stats()
        if not d:
            raise Exception('No running celery workers were found')
    except Exception as e:
        return {'worker': {'ok': False}}
    return {'worker': {'ok': True}}


def celery_check():
    return {'celery': [celery_worker_check()]}
