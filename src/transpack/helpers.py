""" Various helper methods """

from django.core.signing import Signer, BadSignature
from django.conf import settings

import os
import base64
import binascii

def get_size(path):
    """
    Returns the size of a directory using Python 3.5 PEP 471 os.scandir()
    MUCH faster than os.walk as scandir returnings file attributes along
    with the filename, saving many system calls (2-3x) per attribute
    """
    total = 0
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            total += get_size(entry.path)
        else:
            total += entry.stat(follow_symlinks=False).st_size
    return total

def validate_b64folder(folder64):
    """
    Validates the given base64 folder path exists and the filename is valid
    Returns folder name if so
    """
    # Unpack base64 signed folder
    try:
        signed_folder = base64.b64decode(folder64)
    except binascii.Error:
        return False

    # Verify signature
    signer = Signer()
    try:
        folder = signer.unsign(signed_folder)
    except BadSignature:
        return False

    # Validate folder exists on filesystem
    base_dir = settings.TRANSMISSION_DOWNLOAD_DIR
    if os.path.isdir("{}{}".format(base_dir, folder)):
        return folder
    else:
        return False
