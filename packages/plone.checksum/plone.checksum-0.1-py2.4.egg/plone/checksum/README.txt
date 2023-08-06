General
-------

This package defines a `ChecksumManager` that's used to calculate,
access, and write checksums to individual fields of an object.  Let's
create an Archetypes `Document` content object:

  >>> folder = self.folder
  >>> folder.invokeFactory('Document', 'mydocument', title='My Document')
  'mydocument'
  >>> doc = folder.mydocument

We can now request a ChecksumManager for an object like so:

  >>> from plone.checksum import IChecksumManager
  >>> manager = IChecksumManager(doc)

The manager maps field names to `IChecksum` objects:

  >>> sorted(manager.keys())
  ['allowDiscussion', 'contributors', 'creation_date', 'creators', 'description', 'effectiveDate', 'excludeFromNav', 'expirationDate', 'id', 'language', ..., 'text', 'title']

We keep the checksum for our object's title around as `original` for
the following tests:

  >>> original = str(manager['title'])
  >>> print original
  f796979e29808c04f422574ac403baeb

We can manually invoke the checksum calculation using the `calculate`
method of checksum objects.  The stored and the calculated checksum
should certainly be the same at this point:

  >>> print manager['title'].calculate()
  f796979e29808c04f422574ac403baeb

Checksums are written (and attached to the object that has the field)
using the `update` method:

  >>> manager['title'].update('something else')
  >>> print manager['title']
  something else

Let's revert back to the correct checksum by using the
`update_checksums` method on the checksum manager:

  >>> manager.update_checksums()
  >>> print manager['title']
  f796979e29808c04f422574ac403baeb

Finally, we'll change the title and verify that the checksum has
changed:

  >>> doc.setTitle('something else')
  >>> print manager['title'].calculate()
  6c7ba9c5a141421e1c03cb9807c97c74

However, the stored checksum is still the old value.  We need to fix
this by firing the modified event again.  This time, we won't fire the
event ourselves, we'll call `processForm`, which fires the event for
us:

  >>> print manager['title']
  f796979e29808c04f422574ac403baeb
  >>> doc.processForm()
  >>> print manager['title']
  6c7ba9c5a141421e1c03cb9807c97c74
 
By the way, this is equal to:

  >>> import md5
  >>> print md5.new('something else').hexdigest()
  6c7ba9c5a141421e1c03cb9807c97c74

Files
-----

Let's create a File content object: After that, we look at the
checksum for the `file` field:

  >>> from StringIO import StringIO
  >>> folder.invokeFactory('File', 'myfile')
  'myfile'
  >>> file = folder.myfile
  >>> manager = IChecksumManager(file)
  >>> print manager['file']
  d41d8cd98f00b204e9800998ecf8427e

Let's fill the content's `file` field with some contents:

  >>> contents = StringIO('some contents')
  >>> file.setFile(contents)
  >>> print manager['file'].calculate()
  220c7810f41695d9a87d70b68ccf2aeb

If we set the file's contents to something else, the checksum changes:

  >>> contents = StringIO('something else')
  >>> file.setFile(contents)
  >>> print manager['file'].calculate()
  6c7ba9c5a141421e1c03cb9807c97c74

The same should also work for larger files.  Note that the contents
here are stored in a different structure internally:

  >>> contents = StringIO('some contents, ' * 10000)
  >>> file.setFile(contents)
  >>> print manager['file'].calculate()
  8d43d3687f3684666900db3945712e90

Let's make sure once again that the checksum changes when we set
another large file.  This time around we'll upload the file using the
`PUT` method and we'll make sure that the checksum calculation has
been triggered:

  >>> from Products.Archetypes.tests.utils import aputrequest
  >>> contents = StringIO('something else, ' * 10000)
  >>> request = aputrequest(contents, 'text/plain')
  >>> request.processInputs()
  >>> ignore = file.PUT(request, request.RESPONSE)
  >>> str(file.getFile()) == contents.getvalue()
  True
  >>> print manager['file']
  4003a21edc0b8d93bda0ce0c4fa71cfa

This is again the same as:

  >>> print md5.new(contents.getvalue()).hexdigest()
  4003a21edc0b8d93bda0ce0c4fa71cfa
