import csv
import zipfile
from zope.component import getUtility
from Acquisition import aq_inner
from DateTime import DateTime
from StringIO import StringIO
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from slc.dublettefinder.interfaces import IDubletteFinderConfiguration

class findDuplicateFiles(BrowserView):

    def query(self, context, **kwargs):

        dfsettings = getUtility(IDubletteFinderConfiguration, 
                                name='dublettefinder_config')
        deviance = dfsettings.allowable_size_deviance
        # XXX: Refactor to give a nice report. Bring in filename matches as
        # well.

        pc = getToolByName(self, 'portal_catalog')
        # A bit of a hack to find all the objects that has the 'getFileSizes'
        # field.  
        fsquery = {'query':0,
                   'range':'min'
                  }
        ps = pc(getFileSizes=fsquery)
        dupe_dict = {}
        for p in ps:
            for s in p.getFileSizes:
                # get size matches
                fsquery = {'query':(s-deviance,s+deviance),
                           'range':'min:max' }
                rs = pc(getFileSizes=fsquery)
                dupe_dict[p.getURL()] = {}
                for b in rs:
                    if b.getURL() == p.getURL():
                        continue 
                    if dupe_dict[p.getURL()].get(b.getURL(), []):
                        dupe_dict[p.getURL()][b.getURL()].append('size')
                    else:
                        dupe_dict[p.getURL()][b.getURL()] = ['size']
                
            # Get name matches
            rs = pc(getFileNames=p.getFileNames)
            for b in rs:
                if b.getURL() == p.getURL():
                    continue 
                if dupe_dict[p.getURL()].get(b.getURL(), []):
                    dupe_dict[p.getURL()][b.getURL()].append('name')
                else:
                    dupe_dict[p.getURL()][b.getURL()] = ['name']

        out = StringIO()
        file_name = 'possible_file_duplications-%s' % DateTime().strftime('%d-%m-%y')
        writer = csv.writer(out)
        row = ['Object Path', 'Object(s) containing possible duplicate file(s)', 'Match criteria']
        writer.writerow(row)
        for k in dupe_dict.keys():
            i = 0 
            for key, value in dupe_dict[k].items():
                if i == 0:
                    row = [k, key, ' '.join(value)]
                    writer.writerow(row)
                else:
                    row = ['', key, ' '.join(value)]
                    writer.writerow(row)
                i += 1

        out.seek(0)
        csv_content = out.read()
        sio = StringIO()
        archive = zipfile.ZipFile(sio, 'w', zipfile.ZIP_DEFLATED)
        zinfo = zipfile.ZipInfo('%s.csv' % file_name)
        archive.writestr(zinfo, csv_content)
        archive.close()
        zipped_csv_content = sio.getvalue()
        sio.close()
        file_name = 'attachment; filename="%s.zip"' % file_name
        self.context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/zip')
        self.context.REQUEST.RESPONSE.setHeader('Content-Disposition', file_name)
        self.context.REQUEST.RESPONSE.setHeader('Content-Length', str(len(zipped_csv_content)))
        return zipped_csv_content
             

    def __call__(self, **kwargs):
        context = aq_inner(self.context)
        return self.query(context, **kwargs)


