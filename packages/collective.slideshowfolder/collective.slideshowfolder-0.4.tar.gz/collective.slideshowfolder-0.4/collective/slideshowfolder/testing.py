from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from Products import CMFPlone

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class InstallLayer(tcl_ptc.BasePTCLayer):

    _configure_portal = True

    def afterSetUp(self):
        ZopeTestCase.installProduct('slideshowfolder')
        ZopeTestCase.installPackage('collective.slideshowfolder')
        self.addProfile('collective.slideshowfolder:default')

        self.loginAsPortalOwner()
        self.portal.invokeFactory(
            type_name='Folder', id='images', title='Images')
        self.portal.images.invokeFactory(
            type_name='Image', id='foo-image-title',
            title='Foo Image Title',
            description='Foo Image description',
            image=self.portal['document_icon.gif']._readFile(False))

        self.login()
        self.portal.portal_membership.getMemberById(
            ptc.default_user).setProperties(fullname='Foo Full Name')
        self.folder.invokeFactory(
            type_name='Folder', id='slideshow', title='Slideshow')
        self.folder.slideshow.invokeFactory(
            type_name='Image', id='bar-image-title',
            title='Bar Image Title',
            description='Bar Image description')
        
install_layer = InstallLayer([ptc.PloneTestCase.layer])
    
