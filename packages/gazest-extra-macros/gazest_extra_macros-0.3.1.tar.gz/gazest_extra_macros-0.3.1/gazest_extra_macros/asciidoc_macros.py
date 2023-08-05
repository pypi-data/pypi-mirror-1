
def enable(page, val):
    # we import only now because support is optional
    asciidoc_mod = __import__('asciidoc.asciidoc')
    from util import make_adapter

    def render(body):
        src = NamedTemporaryFile()
        dst = NamedTemporaryFile("r")

        src.write(body)
        src.flush()
        
        asciidoc_mod.asciidoc.asciidoc("xhtml11",
                                       "article",
                                       [], src.name, dst.name, ["-s"])
        return dst.read()
 
    page.html_renderer = make_adapter(render)
    return ""
