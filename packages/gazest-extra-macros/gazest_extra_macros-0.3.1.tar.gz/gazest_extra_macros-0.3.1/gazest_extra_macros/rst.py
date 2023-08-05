
def enable(page, val):
    # we import only now because support is optional
    from docutils.core import publish_string
    settings = dict(file_insertion_enabled=False,
                    raw_enabled=False)

    def render(body):
        return publish_string(source=body,
                              settings_overrides=settings,
                              writer_name='html')

    page.html_renderer = render
    return ""
