from zope.interface import Interface

class ICollageSliderLayer(Interface):
    """
    marker interface for collage slider layer
    """

class ICollageSliderUtil(Interface):
    
    def should_include():
        """
        if the slider files should be included
        """
