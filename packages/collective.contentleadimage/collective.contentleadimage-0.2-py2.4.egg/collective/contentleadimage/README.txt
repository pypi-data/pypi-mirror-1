collective.contentleadimage Package Readme
==========================================

Overview
--------

This products adds complete support for adding descriptive image to any Archetypes based 
content in Plone site. Each object has new tab "Edit lead image", which allows to upload 
new or remove current image. It is similar behaviour as Plone News Item (you can add image
to news item and this image is displayed in news item overview listing.

There is folder_leadimage_view page template, which can be used to list all items in the folder
together with images attached. 

There is configuration control panel, where you can set maximum width and height of the uploaded
images. The widht and height is applied on each image upload (image is automatically resized).

There is FieldIndex and metadata in portal_catalog: hasContentLeadImage (True/False).

Tests of the package

    >>> import os
    >>> current_file = globals()['__file__']
    >>> tests_dir, _ = os.path.split(current_file)
    >>> tests_dir = os.path.join(tests_dir, 'tests')

    >>> _ = self.folder.invokeFactory('Document', 'doc1')
    >>> doc = self.folder['doc1']
    >>> doc.update(title='The Document')
    >>> doc.processForm()

    >>> import PIL
    >>> import os
    >>> from StringIO import StringIO
    >>> from Products.CMFCore.utils import getToolByName
    >>> from collective.contentleadimage.interfaces import ILeadImageable
    >>> from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
    >>> from collective.contentleadimage.interfaces import ILeadImage
    >>> portal_setup = getToolByName(self.portal, 'portal_setup')
    >>> _ = portal_setup.runAllImportStepsFromProfile('profile-collective.contentleadimage:default')
    >>> ILeadImageable.providedBy(doc)
    True
    
    >>> test_image = os.path.join(tests_dir, 'test_41x41.jpg')
    >>> raw_image = open(test_image, 'rb').read()
    
    >>> adapted  = ILeadImage(doc)
    >>> adapted.setImage(StringIO(raw_image))

    >>> stored = adapted.getImage()
    
    Got OFS.OFS.Image object
    
    >>> image = PIL.Image.open(StringIO(str(stored.data)))
    >>> image.size
    (41, 41)
    
    Set another size of the image
    
    >>> self.loginAsPortalOwner()
    >>> cp = ILeadImagePrefsForm(self.portal)
    >>> cp.image_height = 20
    >>> cp.image_width  = 20
    >>> self.logout()
    >>> self.login()

    And store image again
    
    >>> adapted.setImage(StringIO(raw_image))
    >>> image = PIL.Image.open(StringIO(str(adapted.getImage().data)))
    >>> image.size
    (20, 20)
    
    Finally remove the image
    
    >>> adapted.removeImage()
    >>> not not adapted.getImage()
    False