Tests of the package

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
    
    >>> test_image = '/Users/naro/work/collective.contentleadimage/collective/contentleadimage/tests/test_41x41.jpg'
    >>> raw_image = open(test_image, 'rb').read()
    
    >>> adapted  = ILeadImage(doc)
    >>> adapted.setImage(StringIO(raw_image), 'image/jpeg')

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
    
    >>> adapted.setImage(StringIO(raw_image), 'image/jpeg')
    >>> image = PIL.Image.open(StringIO(str(adapted.getImage().data)))
    >>> image.size
    (20, 20)
    
    Finally remove the image
    
    >>> adapted.removeImage()
    >>> not not adapted.getImage()
    False