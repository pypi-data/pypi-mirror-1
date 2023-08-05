
def enable(page, val):
    # we import only now because support is optional
    from textile import textile

    def render(body):
        # python-textile chokes on unicode
        body = textile(body.encode("utf-8"))
        return unicode(body, "utf-8")

    page.html_renderer = render
    return ""
