

def _n_repeat(n, msg, pad=", "):
    return pad.join([msg for i in range(n)])


def once(page, msg):
    return msg


def twice(page, msg):
    return _n_repeat(2, msg)


def thrice(page, msg):
    return _n_repeat(3, msg)

