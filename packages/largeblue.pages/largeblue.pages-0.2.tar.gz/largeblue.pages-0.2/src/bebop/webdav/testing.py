

def printEvent(event):
    obj = getattr(event, 'object', None)
    if obj is None :
        name = ''
    else :
        name = getattr(obj, '__name__', 'unnamed')
    print "Event log:", event.__class__.__name__, name
