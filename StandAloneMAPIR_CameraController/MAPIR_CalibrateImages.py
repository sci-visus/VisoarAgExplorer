import os

from MAPIR_Processing import *
#import breeze_resouces

modpath = os.path.dirname(os.path.realpath(__file__))
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    try:

        myapp = MAPIR_ProcessingCLI()


    except Exception as e:
            print(e)

