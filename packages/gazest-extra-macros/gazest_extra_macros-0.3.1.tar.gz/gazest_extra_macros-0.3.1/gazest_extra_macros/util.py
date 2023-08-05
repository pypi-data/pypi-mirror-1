
import string
import random
from tempfile import NamedTemporaryFile

def make_marker():
    return "0%s1" % "".join([random.choice(string.letters)
                             for i in range(12)])

def find_marker(body):
    """ Produce a marker suitable for tagging elements that is not
    already present in body. """
    mrk = make_marker()
    while body.find(mrk) != -1:
        mrk = make_marker()
    return mrk

def make_adapter(render_funct):
    """ Return a wraper function that removes non-alnum markup before
    calling render_funct().

    Some rendering engines are incompatible with Gazest internal
    representation.  Instead of hacking a new internal representation
    for every possible renderer, this function re-tags the text to
    render with alnum only markup.  This can't possibly clash since
    the resulting markup look like perfectly normal prose but it is
    inefficient so we only use it with renderers that do clash."""

    def wrapper(body):
    
        omrk = find_marker(body)
        body = body.replace("[[[", omrk)
        cmrk = find_marker(body)
        body = body.replace("]]]", cmrk)

        body = render_funct(body)

        body = body.replace(omrk, "[[[")
        body = body.replace(cmrk, "]]]")
        return body

    return wrapper
