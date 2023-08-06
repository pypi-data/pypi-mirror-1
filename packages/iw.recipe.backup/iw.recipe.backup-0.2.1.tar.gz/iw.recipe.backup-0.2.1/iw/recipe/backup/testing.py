import os

DEBUG = os.path.join(os.path.dirname(__file__), 'DEBUG')

def set_input(response):
    open(DEBUG, 'w').write(str(response))

def get_input(msg):
    if not os.path.exists(DEBUG):
        return None 
    res = open(DEBUG).read()
    print '%s %s' % (msg, res)
    return res

def remove_input():
    os.remove(DEBUG)

