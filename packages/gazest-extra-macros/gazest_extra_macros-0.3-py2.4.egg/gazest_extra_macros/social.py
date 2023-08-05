
from gazest.lib import helpers as h

def _reddit(page, style):
    url = h.fq_url_for(controller="/wiki", action="view", slug=page.slug)
    return """<script>reddit_url='%s'</script>
<script>reddit_title='%s'</script>
<script language="javascript"
        src="http://reddit.com/button.js?t=%d"></script>""" % (url,
                                                               page.title,
                                                               style)

def reddit_small(page, arg):
    return _reddit(page, 1)


def reddit_big(page, arg):
    return _reddit(page, 2)


def reddit_alien(page, arg):
    return _reddit(page, 3)


def _digg(page, style):
    url = h.fq_url_for(controller="/wiki", action="view", slug=page.slug)
    return """<script type="text/javascript">
 digg_title = '%s';
 digg_url = '%s';
 digg_skin = '%s';
 </script>
 <script src="http://digg.com/tools/diggthis.js"
         type="text/javascript"></script>""" % (page.title, url, style)


def digg_small(page, arg):
    return _digg(page, "compact")


def digg_big(page, arg):
    return _digg(page, "normal")


def stumbleupon(page, arg):
    # TODO: package the button image and find a way to install it globally
    url = h.fq_url_for(controller="/wiki", action="view", slug=page.slug)
    return """<a href="http://www.stumbleupon.com/submit?url=%s&title=%s"
                 ><img border=0 src="/images/stumble1.gif"
                       alt="StumbleUpon Toolbar"></a>""" % (url, page.title)
