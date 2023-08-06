# -*- coding: utf-8 -*-

"""Generate a name for a temprary pickled file to hold the fileinfo data.
"""


from os.path import expanduser, normpath
from tempfile import NamedTemporaryFile


pickledDataPath = normpath(expanduser("~/fileinfo_data_for_django.pickle"))

if False:
    homeDir = normpath(expanduser("~"))
    f = NamedTemporaryFile(
        mode="w", suffix=".pickle", prefix="fileinfo_data_", dir=homeDir)
