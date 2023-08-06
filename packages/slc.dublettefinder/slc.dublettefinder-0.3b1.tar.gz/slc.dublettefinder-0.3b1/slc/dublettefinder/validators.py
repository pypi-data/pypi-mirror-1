from zope.component import getUtility

from Acquisition import aq_base
from types import FileType
try:
    from ZPublisher.HTTPRequest import FileUpload
except ImportError:
    FileUpload = FileType

from Products.CMFCore.utils import getToolByName
from Products.validation.config import validation
from Products.validation.interfaces.IValidator import IValidator

from interfaces import IDubletteFinderConfiguration

validation_override_checkbox_tal = """
<br clear="all"/>
<input type="checkbox" 
    id="ignoreValidationWarning" 
    name="ignoreValidationWarning:boolean" 
    value="on" 
    class="noborder"/>

<input type="hidden" 
    name="ignoreValidationWarning:boolean:default" 
    value="" 
    originalvalue=""/>

<label for="ignoreValidationWarning" 
    class="formQuestion">
    Ignore warning
</label>

<div id="ignoreValidationWarning_help">
    Ignore the duplication warning when uploading the file
</div>
<br clear="all"/>
""" 

title_validation_override_checkbox_tal = """
<br clear="all"/>
<input type="checkbox" 
    id="ignoreTitleValidationWarning" 
    name="ignoreTitleValidationWarning:boolean" 
    value="on" 
    class="noborder"/>

<input type="hidden" 
    name="ignoreTitleValidationWarning:boolean:default" 
    value="" 
    originalvalue=""/>

<label for="ignoreTitleValidationWarning" 
    class="formQuestion">
    Ignore warning
</label>

<div id="ignoreValidationWarning_help">
    Ignore the duplication warning when uploading the file
</div>
<br clear="all"/>
"""


class isUniqueObjectName:
    """ Fails when the file *content type* name already exists in ZODB. Can be ignored with
        'ignoreTitleValidationWarning=True' keyword parameter or REQUEST value.
    """
    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kw):
        dfsettings = getUtility(IDubletteFinderConfiguration, name='dublettefinder_config')
        if not dfsettings.check_object_name:
            return 1

        instance = kw['instance']
        request = instance.REQUEST

        if not value or request.get('ignoreTitleValidationWarning'):
            return 1

        # Search for existing objects in the ZODB with the same name.
        catalog = getToolByName(instance, 'portal_catalog')
        query = {'Title':  value, 
                 'portal_type' : instance.portal_type }
        brains = catalog(query)

        refs = instance.getReferences()
        back_refs = instance.getBackReferences()
        all_refs = refs + back_refs
        ref_paths = ['/'+r.absolute_url(1) for r in all_refs]

        # Remove false positives
        brains = [b for b in brains if b.getPath() != '/%s' % \
            instance.absolute_url(1) and b.getPath() not in ref_paths]   

        if brains:
            instance.REQUEST.set('show_title_validation_override', 1)
            s = "Warning: An similar object with the same title \
                '%s', already exists in the database." % value
            i = 0
            for b in brains:
                i += 1
                path = '%s%s' % (instance.portal_url(), b.getPath())
                s += """<br/>%d) <a target="_blank" href="%s/view"> %s </a> \
                     """ % (i, path, path)
            s += title_validation_override_checkbox_tal 
            return (s)
        return 1
        
validation.register(isUniqueObjectName('isUniqueObjectName', title='', description=''))


class isUniqueFileName:
    """ Fails when file Name already exists in ZODB. Can be ignored with
        'ignoreValidationWarning=True' keyword parameter or REQUEST value.
    """
    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kw):
        dfsettings = getUtility(IDubletteFinderConfiguration, name='dublettefinder_config')
        if not dfsettings.check_file_name:
            return 1

        instance = kw['instance']
        request = instance.REQUEST

        if request.get('ignoreValidationWarning'):
            return 1

        if instance.check_id(value.filename):
            # check_id fails, so it's not necessary to add our own validation
            # error since it will be ignored. Also, we don't want
            # show_validation_override to be set.
            return 1

        # Search for existing files in the ZODB with the same name.
        catalog = getToolByName(instance, 'portal_catalog')
        query = {'getFileNames': value.filename}
        brains = catalog(query)

        refs = instance.getReferences()
        back_refs = instance.getBackReferences()
        all_refs = refs + back_refs
        ref_paths = ['/'+r.absolute_url(1) for r in all_refs]

        # Remove false positives 
        brains = [b for b in brains if b.getPath() != '/%s' % \
            instance.absolute_url(1) and b.getPath() not in ref_paths]   

        if brains:
            instance.REQUEST.set('show_validation_override', 1)
            s = "Warning: A file with the same name %s already \
                exists in the database." % value.filename
            i = 0
            for b in brains:
                i += 1
                path = '%s%s' % (instance.portal_url(), b.getPath())
                s += """<br/>%d) <a target="_blank" href="%s/view"> %s </a> \
                     """ % (i, path, path)
            s += validation_override_checkbox_tal 
            return (s)
        return 1
        
validation.register(isUniqueFileName('isUniqueFileName', title='', description=''))


class isUniqueFileSize:
    """ Fails when a file with the same size already exists in ZODB. Can be overridden with
        'ignoreValidationWarning=True' keyword parameter or REQUEST value.
    """
    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kw):
        dfsettings = getUtility(IDubletteFinderConfiguration, name='dublettefinder_config')
        if not dfsettings.check_file_size:
            return 1

        instance = kw['instance']
        request = instance.REQUEST

        if request.get('ignoreValidationWarning'):
            return 1

        if isinstance(value, FileUpload) or type(value) is FileType \
          or hasattr(aq_base(value), 'tell'):
            value.seek(0, 2) # eof
            size = value.tell()
            value.seek(0)
        elif hasattr(value, 'size'):
            size = value.size
            if callable(size): size = size()
        else:
            try:
                size = len(value)
            except TypeError:
                size = 0

        size = float(size)
        catalog = getToolByName(instance, 'portal_catalog')
        dfsettings = getUtility(IDubletteFinderConfiguration, name='dublettefinder_config')
        deviance = dfsettings.allowable_size_deviance
        fsquery = {'query':(size-deviance, size+deviance),
                   'range':'min:max' }

        query = {'getFileSizes': fsquery}
        brains = catalog(query)

        refs = instance.getReferences()
        back_refs = instance.getBackReferences()
        all_refs = refs + back_refs
        ref_paths = ['/'+r.absolute_url(1) for r in all_refs]

        # Remove false positives 
        brains = [b for b in brains if b.getPath() != '/%s' % \
            instance.absolute_url(1) and b.getPath() not in ref_paths]   

        if brains:
            instance.REQUEST.set('show_validation_override', 1)
            s = "Warning: A file with the same or similar size already \
                exists in the database." 
            i = 0
            for b in brains:
                i += 1
                path = '%s%s' % (instance.portal_url(), b.getPath())
                s += """<br/>%d) <a target="_blank" href="%s/view"> %s </a> \
                     """ % (i, path, path)
            s += validation_override_checkbox_tal 
            return (s)
        return 1
        

validation.register(isUniqueFileSize('isUniqueFileSize', title='', description=''))

