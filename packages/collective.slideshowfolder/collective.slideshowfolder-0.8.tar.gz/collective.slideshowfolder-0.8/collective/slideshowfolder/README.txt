.. -*-doctest-*-

==========================
collective.slideshowfolder
==========================

Somtimes useful extensions to Products.slideshowfolder

SlideshowImage
==============

The SlideshowImage content type uses a reference to an existing normal
image somewhere else in the site to act as a kind of link or alias.
This allows for the creation of a folder as a slideshowfolder that
displays images that are actually stored elsewhere.

Start with a couple of normal folders and a normal image.

    >>> portal.images
    <ATFolder at /plone/images>
    >>> portal.images.contentValues()
    [<ATImage at /plone/images/foo-image-title>]
    >>> foo_image = portal.images['foo-image-title']

    >>> folder.contentValues()
    [<ATFolder at /plone/Members/test_user_1_/slideshow>]
    >>> folder.slideshow.contentValues()
    [<ATImage at
      /plone/Members/test_user_1_/slideshow/bar-image-title>]

Open a browser and login as a user who can add SlideshowImages.

    >>> from Products.Five import testbrowser
    >>> from Products.PloneTestCase import ptc
    >>> portal.error_log._ignored_exceptions = ()
    >>> member_browser = testbrowser.Browser()
    >>> member_browser.handleErrors = False
    >>> member_browser.open(portal.absolute_url())
    >>> member_browser.getLink('Log in').click()
    >>> member_browser.getControl(
    ...     'Login Name').value = ptc.default_user
    >>> member_browser.getControl(
    ...     'Password').value = ptc.default_password
    >>> member_browser.getControl('Log in').click()
    >>> member_browser.open(folder.slideshow.absolute_url())

Add a SlideshowImage.  Set the "Image Reference" field to the real image
in the images folder.

    >>> member_browser.getLink(
    ...     url='createObject?type_name=SlideshowImage').click()
    >>> member_browser.getControl(
    ...     'Image Reference').value = foo_image.UID()

Since all values are taken from the referenced image, none of the
normal image fields are editable.

    >>> member_browser.getControl('Title')
    Traceback (most recent call last):
    LookupError: label 'Title'

    >>> member_browser.getControl('Description')
    Traceback (most recent call last):
    LookupError: label 'Description'

    >>> member_browser.getControl(name='image_file')
    Traceback (most recent call last):
    LookupError: name 'image_file'

    >>> member_browser.getControl('Creators')
    Traceback (most recent call last):
    LookupError: label 'Creators'

Save the new SlideshowImage.

    >>> member_browser.getControl('Save').click()

The values for the fields are pulled in from the referenced image.

    >>> print member_browser.contents
    <...
    ...Changes saved...
    ...Foo Image Title...
    ...Foo CreÃtor...
    ...Foo Image description...
    >>> member_browser.getLink('Click to view full-size image')
    <Link text='Foo Image Title[IMG] [IMG]
    Click to view full-size image...'
    url='http://nohost/plone/Members/test_user_1_/slideshow/foo-image-title/image_view_fullscreen'>
    >>> member_browser.open(
    ...     folder.slideshow['foo-image-title'].absolute_url())
    >>> print member_browser.contents
    GIF...

The catalog also reflects the data from the referenced image.

    >>> len(portal.portal_catalog(
    ...     Type='Slideshow Image',
    ...     Description='Foo Image description'))
    1

The catalogged and indexed values for the fields are also updated
when the original image is edited.

Open a browser and log in as the image's creator.

    >>> owner_browser = testbrowser.Browser()
    >>> owner_browser.handleErrors = False
    >>> owner_browser.open(portal.absolute_url())
    >>> owner_browser.getLink('Log in').click()
    >>> owner_browser.getControl(
    ...     'Login Name').value = ptc.portal_owner
    >>> owner_browser.getControl(
    ...     'Password').value = ptc.default_password
    >>> owner_browser.getControl('Log in').click()

Change the image metadata.

    >>> owner_browser.open(foo_image.absolute_url()+'/edit')
    >>> owner_browser.getControl(
    ...     'Description').value = 'Foo Image edited'
    >>> owner_browser.getControl('Save').click()

The catalog now reflects the changes for the SlideshowImage that
references the image.

    >>> len(portal.portal_catalog(
    ...     Type='Slideshow Image',
    ...     Description='Foo Image description'))
    0

    >>> len(portal.portal_catalog(
    ...     Type='Slideshow Image',
    ...     Description='Foo Image edited'))
    1

Slideshow Folders
=================

SlideshowImages is in a folder using the slideshowfolder view behave
just like regular images.

Make the folder into a slideshowfolder.

    >>> member_browser.open(folder.slideshow.absolute_url())
    >>> member_browser.getLink('Make slideshow').click()
    >>> print member_browser.contents
    <...
    ...This folder is now designated a slideshow...

Check that the SlideshowImage is included in the slideshow by
inspecting the JavaScript.  The collective.slideshowfolder package
also extends the caption to include the image's creator for credit.

    >>> member_browser.open(
    ...     folder.slideshow.absolute_url()+'/slideshow_settings.js')
    >>> print member_browser.contents
    registerPloneFunction...
    ...http://nohost/plone/Members/test_user_1_/slideshow/bar-image-title/image_large...
    ...Photo: Foo Full NÃme...
    ...Bar ImÃge description...
    ...http://nohost/plone/Members/test_user_1_/slideshow/foo-image-title/image_large...
    ...Photo: Foo CreÃtor...
    ...Foo Image edited...

