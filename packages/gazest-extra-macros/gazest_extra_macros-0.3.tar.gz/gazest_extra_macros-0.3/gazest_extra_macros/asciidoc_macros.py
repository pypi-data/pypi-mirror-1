
import string
import random

def _make_marker():
    return "0%s1" % "".join([random.choice(string.letters)
                             for i in range(12)])


def _find_marker(body):
    """ Produce a marker suitable for tagging elements that is not
    already present in body. """
    mrk = _make_marker()
    while body.find(mrk) != -1:
        mrk = _make_marker()
    return mrk


def enable(page, val):
    # we import only now because support is optional
    asciidoc_mod = __import__('asciidoc.asciidoc')
    from tempfile import NamedTemporaryFile

    def render(body):
        # Asciidoc is not compatible with Gazest stubs so we re-tag
        omrk = _find_marker(body)
        body = body.replace("[[[", omrk)
        cmrk = _find_marker(body)
        body = body.replace("]]]", cmrk)
        
        src = NamedTemporaryFile()
        dst = NamedTemporaryFile("r")

        src.write(body)
        src.flush()
        
        asciidoc_mod.asciidoc.asciidoc("xhtml11",
                                       "article",
                                       [], src.name, dst.name, ["-s"])
        body = dst.read()
        body = body.replace(omrk, "[[[")
        body = body.replace(cmrk, "]]]")
        return body
 
    page.html_renderer = render
    return ""
