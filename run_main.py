import os
import sys
import warnings
warnings.filterwarnings("ignore")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
path = resource_path('main.py')

print('Running main.py')
os.system(f'python3 {path}')
print('Successfully terminated main.py')