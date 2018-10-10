import os
from random import randrange, getrandbits
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


def is_prime(n, k=128):
    """ Test if a number is prime
        Args:
            n -- int -- the number to test
            k -- int -- the number of tests to do
        return True if n is prime
    """
    # Test if n is not even.
    # But care, 2 is prime !
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    # find r and s
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    # do k tests
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True


def generate_prime_candidate(length):
    """ Generate an odd integer randomly
        Args:
            length -- int -- the length of the number to generate, in bits
        return a integer
    """
    # generate random bits
    p = getrandbits(length)
    # apply a mask to set MSB and LSB to 1
    p |= (1 << length - 1) | 1
    return p


def generate_prime_number(length=1024):
    """ Generate a prime
        Args:
            length -- int -- length of the prime to generate, in          bits
        return a prime
    """
    p = 4
    # keep generating while the primality test fail
    while not is_prime(p, 128):
        p = generate_prime_candidate(length)
    return p
