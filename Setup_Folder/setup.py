import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
reqs_path = resource_path('requirements.txt')

print('Reading requirements.txt')

os.system(f'conda create --name TransportationManager --file {reqs_path}')

print('Successfully created environment')