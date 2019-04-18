import base64

separator = '$$'


def encode_task_uuid(*args):
    return base64.encodebytes(separator.join(args).encode()).decode()


def decode_task_uuid(task):
    return base64.decodebytes(task.encode()).decode().split(separator)
