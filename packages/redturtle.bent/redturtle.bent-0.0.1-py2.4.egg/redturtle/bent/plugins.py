from time import time
from zope.app.component.hooks import getSite
import traceback

def timeplugin(function, *args, **kwargs):
    """
    Time plugin for mr.bent which allows you to track function times.
    """
    bent_trace = traceback.extract_stack()
    stack_info = ''
    for n, frame in enumerate(bent_trace):
        if frame[0].endswith('monkey.py') and frame[2] == 'wrapper':
            stack_info = bent_trace[n-1]
            break
    t1 = time()
    res = function(*args, **kwargs)
    t2 = time()
    timestamp = "%.4f" % (t2-t1)
    print "%s: %s - called from %s, line %s" % (function.__name__, timestamp, stack_info[0], stack_info[1])  
    return timestamp,res
