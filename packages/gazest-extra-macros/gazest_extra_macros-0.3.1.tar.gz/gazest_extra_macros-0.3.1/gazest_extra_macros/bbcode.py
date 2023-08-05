
def enable(page, val):
    # we import only now because support is optional
    from gazest_extra_macros import postmarkup
    from util import make_adapter

    page.html_renderer = make_adapter(postmarkup.render_bbcode)
    return ""
