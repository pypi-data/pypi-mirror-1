
import os

if 'set' not in dir(__builtins__):
    from sets import Set as set

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/'))

class Glutton(object):
    "Eat everything."
    def __getattr__(self, name):
        return Glutton()

    def __setattr__(self, name, value):
        pass

    def __call__(self, *args, **kwds):
        pass


def create_empty_file(file_path):
    fd = file(file_path, "w")
    fd.close()

def create_empty_files_in_directory(files, directory):
    for filename in files:
        create_empty_file(os.path.join(directory, filename))
