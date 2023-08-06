from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class InstallLayer(tcl_ptc.BasePTCLayer):

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
            description=u'Foo Image description',
            creators=[u'Foo Cre\xc3tor'],
            image=self.portal['document_icon.gif']._readFile(False))

        self.login()
        self.portal.portal_membership.getMemberById(
            ptc.default_user).setProperties(
            fullname=u'Foo Full N\xc3me') # test unicode
        self.folder.invokeFactory(
            type_name='Folder', id='slideshow', title='Slideshow')
        self.folder.slideshow.invokeFactory(
            type_name='Image', id='bar-image-title',
            title='Bar Image Title',
            description=u'Bar Im\xc3ge description')
        
install_layer = InstallLayer([tcl_ptc.ptc_layer])
    
