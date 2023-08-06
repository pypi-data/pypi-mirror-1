from Products.Archetypes import Field
from Products.PlonePAS import utils

from Products.slideshowfolder import browser

class SlideShowFolderView(browser.SlideShowFolderView):

    def _getImageCaption(self, item):
        caption = super(
            SlideShowFolderView, self)._getImageCaption(item)
        creator = Field.decode(item.Creator, self.context)
        member = self.context.portal_membership.getMemberById(creator)
        if member is not None:
            creator = member.getProperty('fullname').decode(
                utils.getCharset(self.context)) or creator
        return 'Photo: %s, %s' % (creator, caption)
