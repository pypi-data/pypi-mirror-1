import sys
import os

sys.path.append('../..')

import schema

def __call__():
    s = schema.Schema()
    path = os.path.abspath('schema.ini')
    s.read(path)
    return s

if __name__=='__main__':
    print __call__()