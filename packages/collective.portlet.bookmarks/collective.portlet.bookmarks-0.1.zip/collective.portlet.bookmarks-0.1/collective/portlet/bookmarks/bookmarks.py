from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from zope.i18n import translate

from plone.app.kss.plonekssview import PloneKSSView
from plone.app.kss.interfaces import IPloneKSSView
from kss.core import kssaction

from Products.CMFCore.utils import getToolByName
from collective.portlet.bookmarks import BookmarksPortletMessageFactory as _

from zope.interface import implements


class BookmarksView(PloneKSSView):

    implements(IPloneKSSView)

    def doBookmark(self):
        context = self.context

        pm = getToolByName(context, 'portal_membership')
        memberArea = pm.getHomeFolder()

        bookmarks = getattr(memberArea, 'bookmarks', None)
        if bookmarks is None:
            memberArea.invokeFactory('Folder', 'bookmarks')
            bookmarks = getattr(memberArea, 'bookmarks')
            bookmarks.setTitle(translate(_(u'My Bookmarks'),
                               context=self.request))
            bookmarks.reindexObject()

        bookmark = None
        uid = context.UID()
        if not uid in bookmarks.objectIds():
            bookmarks.invokeFactory('Link', uid)
            bookmark = getattr(bookmarks, uid)
            bookmark.setTitle(context.Title())
            bookmark.setRemoteUrl(context.absolute_url())
            bookmark.setLanguage(context.Language())
            bookmark.reindexObject()

        if bookmark is None:
            message = _(u'Bookmark already there')
        else:
            message = _(u'Bookmark added')

        return message

    @kssaction
    def kss_addBookmark(self, portlet_hash):
        """Add a bookmark and refresh portlet"""

        message = self.doBookmark()

        plonecommands = self.getCommandSet('plone')
        plonecommands.issuePortalMessage(message)
        plonecommands.refreshPortlet(portlet_hash)

        return self.render()
