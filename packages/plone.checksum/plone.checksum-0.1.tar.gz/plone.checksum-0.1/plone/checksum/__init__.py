from plone.checksum.interfaces import IChecksumManager, IChecksum

def modified(object, event):
    IChecksumManager(object).update_checksums()
