
def enable(page, val):
    # we import only now because support is optional
    from markdown import markdown

    page.html_renderer = markdown
    return ""
