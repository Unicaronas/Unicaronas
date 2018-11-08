import os
from importlib import import_module
from django.conf import settings


def file_version(file, levels=1):
    """File Version

    From a versioned folder, get the relative file version

    e.g. the version of the file
    /trips/api/versions/v1_2/serializers.py
    is v1.2
    """
    for _ in range(levels):
        file = os.path.dirname(file)
    folder = os.path.basename(file)
    return folder.replace('_', '.')


def local_versioned_url_name(name, file, levels=1):
    name = name.split(':')
    local_version = file_version(file, levels)
    return ':'.join([name[0], local_version] + name[1:])


def get_current_version():
    return settings.REST_FRAMEWORK['DEFAULT_VERSION']


def import_current_version_module(app_label, api_path):
    current_version = get_current_version()
    version_path = f"{app_label}/api/versions/{current_version.replace('.', '_')}"
    path = os.path.join(version_path, api_path).replace('/', '.')
    return import_module(path)
