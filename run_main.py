import os
import sys

path = os.path.join(sys.path[0], 'main.py')

print('Running main.py')
os.system(f'python3 {path}')
print('Successfully terminated main.py')