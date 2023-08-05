
from os import path

def mergepaths(basefilepath, filepath):
    return path.join(path.dirname(basefilepath), filepath)

