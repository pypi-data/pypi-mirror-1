User interface
--------------

The `check_all` lists items where the checksum stored in the ZODB
differs with the checksum that's calculated on the fly:

  >>> self.loginAsPortalOwner()
  >>> check_all = self.portal.unrestrictedTraverse('checksum__check_all')
  >>> print check_all() # doctest: +ELLIPSIS
  The following items failed the checksum test:
  ...

For quite a bunch of objects in our newly created portal, the modified
event was not fired.  Let's use the other view, `update_all` to set
the checksum for all objects to the calculated one:

  >>> update_all = self.portal.unrestrictedTraverse('checksum__update_all')
  >>> print update_all()
  Calculated and stored checksums of ... items.

Now, `check_all` should give us green light:

  >>> print check_all()
  All ... objects verified and OK!

We can generate small reports using the `print_all` view.  Let's say
we're interested in the checksums of the `title` fields of all the
objects in the portal:

  >>> request = self.portal.REQUEST
  >>> print_all = self.portal.unrestrictedTraverse('checksum__print_all')
  >>> request.form['checksum_fields'] = ['title']
  >>> print; print print_all()
  <BLANKLINE>
  ...
  a47176ba668e5ddee74e58c2872659c7 http://nohost/plone/front-page :title
  ...

We can also format the output like we want it.  Available keys are:

  >>> output_form = ('%(checksum)s %(url)s %(fieldname)s '
  ...                '%(content_type)s %(filename)s')
  >>> request.form['checksum_output'] = output_form

Note that `content_type` is only available for files.  And that
`filename` is currently only available for `OFSBlobFile` values, from
the blob_ Product.

This time we'll create a report with all title fields of all our
`File` content objects:

  >>> request.form['checksum_fields'] = ['title']
  >>> request.form['portal_type'] = 'File'
  >>> print print_all()

Oh well, there are no files.  Let's fix this.  We'll create a fake GIF
file:

  >>> contents = 'GIF89a xxx'
  >>> self.folder.invokeFactory('File', 'myfile', file=contents)
  'myfile'
  >>> print print_all()
  d41d8cd98f00b204e9800998ecf8427e http://nohost/plone/Members/test_user_1_/myfile title n/a n/a

When we request a report for the 'file' field, we'll get that extra
`content_type` field in the output:

  >>> request.form['checksum_fields'] = ['file']
  >>> print print_all()
  e429b46baca83aa4a713965f5146f31a http://nohost/plone/Members/test_user_1_/myfile file image/gif n/a

Is this what we expect?  Yes it is:

  >>> import md5
  >>> print md5.new('GIF89a xxx').hexdigest()
  e429b46baca83aa4a713965f5146f31a

If you wanted a md5sum- compatible report of all `BlobFiles` in your
portal, you would visit::

  http://myportal/checksum__print_all?portal_type=BlobFile&checksum_fields:list=file&checksum_output=%(checksum)s%20%20%(filename)s



.. _blob: http://www.plope.com/software/blob
