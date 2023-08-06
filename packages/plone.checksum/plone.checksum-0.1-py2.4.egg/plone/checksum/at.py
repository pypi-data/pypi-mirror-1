"""Archetypes specific checksum calculators and manager.
"""
import md5
import dispatch

from zope import interface, component
import OFS.Image
from Acquisition import aq_base
from Products.Archetypes.interfaces import IBaseObject
try:
    from Products.blob.zopefile import OFSBlobFile
except ImportError:
    class OFSBlobFile:
        pass

from plone.checksum import interfaces

class ChecksumManager(dict):
    interface.implements(interfaces.IChecksumManager)
    component.adapts(IBaseObject)
    
    def __init__(self, context):
        self.context = context
        for field in self.context.Schema().fields():
            checksum = Checksum(field, self.context)
            self[field.getName()] = checksum

    def update_checksums(self):
        for checksum in self.values():
            checksum.update()

class Checksum:
    interface.implements(interfaces.IChecksum)

    def __init__(self, field, object):
        self.field = field
        self.object = object
        self.key = self._make_key()

    def calculate(self):
        value = self.value()
        return self.do_checksum(value).hexdigest()

    @dispatch.generic()
    def do_checksum(self, value):
        """Return md5 object that has the calculated checksum.
        """

    def __str__(self):
        return getattr(aq_base(self.object), self.key, 'n/a')

    def update(self, checksum=None):
        if checksum is None:
            checksum = self.calculate()
        setattr(self.object, self.key, checksum)

    def value(self):
        accessor = self.field.getAccessor(self.object)
        return accessor()

    def _make_key(self):
        return '_plone_checksum_for_%s' % self.field.getName()


@Checksum.do_checksum.when('isinstance(value, object)')
def do_checksum(self, value):
    checksum = md5.new()
    checksum.update(str(value))
    return checksum

@Checksum.do_checksum.when('isinstance(value, OFS.Image.File)')
def do_checksum(self, value):
    checksum = md5.new()
    value = value.data
    if isinstance(value, str):
        checksum.update(value)
    else:
        while value is not None:
            checksum.update(value.data)
            value = value.next
    return checksum

@Checksum.do_checksum.when('isinstance(value, OFSBlobFile)')
def do_checksum(self, value):
    checksum = md5.new()
    file = value.getIterator()
    while True:
        data = file.read(4096)
        if not len(data):
            break
        checksum.update(data)
    file.close()
    return checksum
