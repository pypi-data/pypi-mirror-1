from zope.interface import implements
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Collage.interfaces import ICollageAlias
from collective.easyslider.interfaces import ISliderPage
from collective.collage.easyslider.interfaces import ICollageSliderUtil

class CollageSliderUtil(BrowserView):
    """
    a public traverable utility that checks if a 
    slide is enabled
    """
    implements(ICollageSliderUtil)

    def should_include(self):
        utils = getToolByName(self.context, 'plone_utils')
        for row in self.context.folderlistingFolderContents():
            for column in row.folderlistingFolderContents():
                for item in column.folderlistingFolderContents():
                    if ICollageAlias.providedBy(item):
                        item=item.get_target()
                    if ISliderPage.providedBy(item) or \
                       utils.browserDefault(item)[1][0] == "sliderview":
                        return True        
        return False
        