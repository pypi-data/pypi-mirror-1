# This is a trivial Python module, containing a single function f().

def f(s, val):
    if val < 0:
        raise ValueError, 'val cannot be negative'
    elif val == 42:
        print 'The answer!'
 
    return s * val
