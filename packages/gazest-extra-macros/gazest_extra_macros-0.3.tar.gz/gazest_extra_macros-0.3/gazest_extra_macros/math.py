
_math = __import__('math')

# TODO: this can be processed 'lisp-macro' style

def log(page, val):
    return "%f" % _math.log(float(val))


def sin(page, val):
    return "%f" % _math.sin(float(val))


def cos(page, val):
    return "%f" % _math.cos(float(val))


def tan(page, val):
    return "%f" % _math.tan(float(val))


def floor(page, val):
    return "%f" % _math.floor(float(val))


def ceil(page, val):
    return "%f" % _math.ceil(float(val))

