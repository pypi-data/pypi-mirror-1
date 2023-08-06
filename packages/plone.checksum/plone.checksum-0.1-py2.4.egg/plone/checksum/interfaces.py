from zope import interface
from zope.interface.common.mapping import IIterableMapping

class IChecksumManager(IIterableMapping):
    """A mapping where keys are identifiers and values are `IChecksum`
    objects.
    """
    def update_checksums():
        """Calculate and update all checksums
        """

class IChecksum(interface.Interface):
    def __str__():
        """Read the stored checksum or 'n/a'
        """

    def calculate():
        """Caclculate checksum
        """
    
    def update(checksum=None):
        """Store checksum.  If not given, I will calculate() myself.
        """

    def value():
        """Return the value that our checksum calculation is based on.
        Befware though that this will return all kinds of objects!"""
