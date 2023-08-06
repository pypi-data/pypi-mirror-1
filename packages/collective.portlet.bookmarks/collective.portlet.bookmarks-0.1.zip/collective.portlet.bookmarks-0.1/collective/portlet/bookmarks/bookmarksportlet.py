from zope.interface import Interface
from zope.interface import implements

from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.memoize.instance import memoize

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.bookmarks import BookmarksPortletMessageFactory as _
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFCore.utils import getToolByName


class IBookmarksPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    show_date = schema.Bool(title=_(u"Show date"),
                                 description=_(u"Display modification date "
                                                "of the bookmarked item."),
                                 required=True,
                                 default=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBookmarksPortlet)

    show_date = True

    def __init__(self, show_date=True):
        self.show_date = show_date

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Bookmarks Portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('bookmarksportlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.portal_state = getMultiAdapter((context, request),
                                            name=u'plone_portal_state')

    @property
    def available(self):
        if not self.portal_state.anonymous():
            return True
        return False

    def getBookmarksFolder(self):
        member = self.portal_state.member()
        if member is not None:
            pm = getToolByName(self.context, 'portal_membership')
            memberArea = pm.getHomeFolder()
            return getattr(memberArea, 'bookmarks', None)

    def getBookmarksFolderUrl(self):
        bookmarks = self.getBookmarksFolder()
        if bookmarks is not None:
            return '/'.join(bookmarks.getPhysicalPath())

    def getBookmarks(self):
        """ get the bookmarks for a user """
        path = self.getBookmarksFolderUrl()
        result = []
        if path is not None:
            for book in self.context.portal_catalog.unrestrictedSearchResults(
                                    sort_on='modified',
                                    path=path,
                                    portal_type='Link',
                                    sort_order='reverse'):
                result.append(dict(
                                title = book.pretty_title_or_id,
                                url = book.getRemoteUrl,
                                description = book.Description,
                                date = ulocalized_time(book.ModificationDate,
                                                       long_format=1,
                                                       context=self.context),
                            ))
        return result

    def show_date(self):
        return self.data.show_date

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IBookmarksPortlet)

    def create(self, data):
        return Assignment(**data)

# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IBookmarksPortlet)
