import dispatch
from StringIO import StringIO

import OFS.Image
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
try:
    from Products.blob.zopefile import OFSBlobFile
except ImportError:
    class OFSBlobFile:
        pass

from plone.checksum import IChecksumManager

class BaseView(BrowserView):
    def context():
        def get(self):
            return self._context[0]
        def set(self, context):
            self._context = [context]
        return property(get, set)
    context = context()

    def query(self, versions=True):
        catalog = getToolByName(self, 'portal_catalog')
        repository = getToolByName(self, 'portal_repository', None)
        brains = catalog(**self.request.form)
        items = [b.getObject() for b in brains]
        if repository and versions:
            # I don't want to think about how expensive this may be
            for item in items[:]:
                history = repository.getHistory(item)
                if history:
                    for version in tuple(history)[1:]:
                        version.object._v_checksum_is_old_version = True
                        items.append(version.object)
        return items

class CheckAll(BaseView):
    def __call__(self):
        broken = []

        form = self.request.form
        fields_to_output = form.get('checksum_fields')
        items = self.query()
        for item in items:
            manager = IChecksumManager(item)
            if fields_to_output is None:
                fieldnames = manager.keys()
            else:
                fieldnames = fields_to_output
            for name in fieldnames:
                checksum = manager[name]
                calculated_checksum = checksum.calculate()
                if str(checksum) != calculated_checksum:
                    broken.append(dict(
                        url=item.absolute_url(),
                        field=name,
                        stored=str(checksum),
                        calculated=calculated_checksum,
                        ))

        out = StringIO()
        if broken:
            print >> out, "The following items failed the checksum test:"
            for item in broken:
                print >> out, ("%(field)r from %(url)r: expected %(stored)r, "
                               "got %(calculated)r" % item)
            
        else:
            print >> out, "All %s objects verified and OK!" % len(items)

        return out.getvalue()

class UpdateAll(BaseView):
    def __call__(self):
        items = self.query(versions=False)
        for item in items:
            manager = IChecksumManager(item)
            manager.update_checksums()

        return "Calculated and stored checksums of %s items." % len(items)

class ForgivingDict(dict):
    """A dict that doesn't know KeyError:

      >>> f = ForgivingDict()
      >>> f['foo'] = 'foo'
      >>> f['foo']
      'foo'
      >>> f['bar']
      ''
      >>> '%(foo)s %(bar)s' % f
      'foo '
    """
    def __init__(self, __default__='', **kwargs):
        self.update(kwargs)
        self.default = __default__

    def __getitem__(self, key):
        if self.has_key(key):
            return super(ForgivingDict, self).__getitem__(key)
        else:
            return self.default

class PrintAll(BaseView):
    def __call__(self):
        catalog = getToolByName(self, 'portal_catalog')
        form = self.request.form
        items = self.query()
        fields_to_output = form.get('checksum_fields')
        output = form.get('checksum_output',
                          '%(checksum)s %(url)s :%(fieldname)s')

        out = StringIO()
        for item in items:
            manager = IChecksumManager(item)
            if fields_to_output is None:
                fieldnames = manager.keys()
            else:
                fieldnames = fields_to_output
            for name in fieldnames:
                checksum = manager[name]
                vars = ForgivingDict(__default__='n/a',
                                     url=item.absolute_url(),
                                     checksum=str(checksum),
                                     fieldname=name)
                vars.update(self.extra_info(checksum, checksum.value()))
                print >> out, output % vars

        return out.getvalue()

    @dispatch.generic()
    def extra_info(self, checksum, value):
        """Return a dict with extra info that can be used in the report.
        """

@PrintAll.extra_info.when('isinstance(value, object)')
def extra_info(self, checksum, value):
    return {}

@PrintAll.extra_info.when('isinstance(value, OFS.Image.File)')
def extra_info(self, checksum, value):
    return dict(content_type=value.content_type)

@PrintAll.extra_info.when('isinstance(value, OFSBlobFile)')
def extra_info(self, checksum, value):
    value = checksum.value()
    f = value.data.open()
    filename = f.name
    f.close()
    return dict(filename=filename,
                content_type=value.content_type)
