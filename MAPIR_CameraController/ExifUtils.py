import subprocess
import os

class ExifUtils:

    @staticmethod
    def copy_simple(inphoto, outphoto, startup_info):
        mod_path = os.path.dirname(os.path.realpath(__file__))
        if sys.platform.startswith('win'):
            exifout = subprocess.run(
                [mod_path + os.sep + r'exiftool.exe',  # r'-config', modpath + os.sep + r'mapir.config',
                 r'-overwrite_original_in_place', r'-tagsFromFile',
                 os.path.abspath(inphoto),
                 r'-all:all<all:all',
                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                startupinfo=startup_info).stderr.decode("utf-8")

            data = subprocess.run(
                args=[mod_path + os.sep + r'exiftool.exe', '-m', r'-ifd0:imagewidth', r'-ifd0:imageheight',
                      os.path.abspath(inphoto)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, startupinfo=startup_info).stderr.decode("utf-8")
        else:
            exifout = subprocess.run(
                [mod_path + os.sep + r'exiftool',  # r'-config', modpath + os.sep + r'mapir.config',
                 r'-overwrite_original_in_place', r'-tagsFromFile',
                 os.path.abspath(inphoto),
                 r'-all:all<all:all',
                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                startupinfo=startup_info).stderr.decode("utf-8")

            data = subprocess.run(
                args=[mod_path + os.sep + r'exiftool', '-m', r'-ifd0:imagewidth', r'-ifd0:imageheight',
                      os.path.abspath(inphoto)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, startupinfo=startup_info).stderr.decode("utf-8")

