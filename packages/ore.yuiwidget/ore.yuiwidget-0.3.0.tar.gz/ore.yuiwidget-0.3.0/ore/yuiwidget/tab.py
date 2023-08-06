"""

Usage is to utilize this class as a base class of a viewlet manager

"""

from zope.viewlet import manager
class TabViewletManager( manager.ViewletManagerBase ):
    """
    we should add support for grouping viewlets.
    """

    def render( self ):
        
        header = u'<div class="tabber" id="content-manager">'
        parts = [u'<div class="tabbertab">%s</div>'%(v.render()) for v in self.viewlets]
        footer = u'</div>'
        return u"%s \n %s \n %s"%( header, u'\n'.join( parts ), footer )
