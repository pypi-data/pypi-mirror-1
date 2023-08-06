from plone.app.layout.viewlets.common import PathBarViewlet
from plone.app.layout.links.viewlets import FaviconViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
class BangalorePathBar(PathBarViewlet):
        render = ViewPageTemplateFile("templates/bgl_path_bar.pt")


class BangaloreFavicon(FaviconViewlet):
        render = ViewPageTemplateFile("templates/favicon.pt")
