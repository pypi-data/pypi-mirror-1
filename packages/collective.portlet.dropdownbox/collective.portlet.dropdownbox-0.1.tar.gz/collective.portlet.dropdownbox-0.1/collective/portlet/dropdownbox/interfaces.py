from zope.interface import Interface



class ILinksBuilder(Interface):
    """Build a list of links from a folder
    """

    def links(self):
        """Returns a list of links each as a dictionary
        """
        
        
        
class ILinkItemBuilder(Interface):
    """Build up a link item
    """

    def link_item(self):
        """Return a link as a dictionary based on a brain.
        """