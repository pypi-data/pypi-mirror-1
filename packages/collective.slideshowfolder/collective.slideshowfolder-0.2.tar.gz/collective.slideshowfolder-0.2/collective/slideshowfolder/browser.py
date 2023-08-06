from Products.slideshowfolder import browser

class SlideShowFolderView(browser.SlideShowFolderView):

    def _getImageCaption(self, item):
        caption = super(
            SlideShowFolderView, self)._getImageCaption(item)
        info = self.context.portal_membership.getMemberInfo(
            item.Creator)
        return 'Photo: %s, %s' % (
            info and info['fullname'] or item.Creator,
            caption)
