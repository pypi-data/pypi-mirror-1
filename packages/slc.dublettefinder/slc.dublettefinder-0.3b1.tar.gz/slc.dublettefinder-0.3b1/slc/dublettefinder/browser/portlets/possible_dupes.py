from zope.component import getUtility
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base

from Products.Archetypes.utils import shasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from slc.dublettefinder.interfaces import IDubletteFinderConfiguration

class IPossibleFileDuplicatesPortlet(IPortletDataProvider):
    """ """

class Assignment(base.Assignment):
    implements(IPossibleFileDuplicatesPortlet)

    @property
    def title(self):
        return _(u"Possible File Duplications")

# The renderer is like a view (in fact, like a content provider/viewlet). The
# item self.data will typically be the assignment (although it is possible
# that the assignment chooses to return a different object - see
# base.Assignment).

class Renderer(base.Renderer):
    # render() will be called to render the portlet
    render = ViewPageTemplateFile('possible_dupes.pt')

    @property
    def available(self):
        self.context.Schema().get('fileSizes')
        if shasattr(self.context, 'Schema') and \
                self.context.Schema().get('fileSizes'):
            return 1
        return 0

    def getPossibleDupes(self):
        """ """
        context = self.context
        if not shasattr(context, 'Schema'):
            return

        dfsettings = getUtility(IDubletteFinderConfiguration, name='dublettefinder_config')
        catalog = getToolByName(context, 'portal_catalog')
        title_brains = []

        if dfsettings.check_object_name:
            # Search for existing objects in the ZODB with the same name.
            query = {'Title':  context.Title(), 
                    'portal_type' : context.portal_type }
            title_brains = list(catalog(query))

        name_brains = []
        if dfsettings.check_file_name and context.Schema().get('fileNames'):
            # Search for existing files in the ZODB with the same name.
            names = context.Schema().get('fileNames').getAccessor(context)()
            query = {'getFileNames': names}
            name_brains = list(catalog(query))

        size_brains = []
        if dfsettings.check_file_size and context.Schema().get('fileSizes', []):
            deviance = dfsettings.allowable_size_deviance
            sizes = context.Schema().get('fileSizes').getAccessor(context)()
            for size in sizes:
                fsquery = {'query':(size-deviance, size+deviance),
                        'range':'min:max'
                        }
                query = {'getFileSizes': fsquery}
                size_brains = list(catalog(query))

        brains = title_brains + name_brains + size_brains
        # Remove false positive
        brains = [b for b in brains if b.getPath() != '/%s' % \
            context.absolute_url(1)]

        refs = context.getReferences()
        back_refs = context.getBackReferences()
        all_refs = refs + back_refs
        ref_paths = ['/'+r.absolute_url(1) for r in all_refs]

        unique_brains = []
        unique_brains_paths = []
        for b in brains:
            if b.getPath() not in unique_brains_paths and \
                    b.getPath() not in ref_paths:

                unique_brains.append(b)
                unique_brains_paths.append(b.getPath())

        return unique_brains


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()


