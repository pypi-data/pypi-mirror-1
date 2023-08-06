##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from interfaces import IllegalHTML
from sgmllib import SGMLParser
from htmlentitydefs import entitydefs
from i18n import _

__all__ = ['filter']

def filter( text ):
   """ Strip illegal HTML tags from string text."""
    parser = StrippingParser()
    parser.feed( html )
    parser.close()
    return parser.result
    
class SimpleHTMLParser( SGMLParser ):

    #from htmlentitydefs import entitydefs

    def __init__( self, verbose=0 ):

        SGMLParser.__init__( self, verbose )
        self.savedata = None
        self.title = ''
        self.metatags = {}
        self.body = ''

    def handle_data( self, data ):
        if self.savedata is not None:
            self.savedata = self.savedata + data

    def handle_charref( self, ref ):
        self.handle_data( "&#%s;" % ref )

    def handle_entityref( self, ref ):
        self.handle_data( "&%s;" % ref )

    def save_bgn( self ):
        self.savedata = ''

    def save_end( self ):
        data = self.savedata
        self.savedata = None
        return data

    def start_title( self, attrs ):
        self.save_bgn()

    def end_title( self ):
        self.title = self.save_end()

    def do_meta( self, attrs ):
        name = ''
        content = ''

        for attrname, value in attrs:
            value = value.strip()
            if attrname == "name":
                name = value.capitalize()
            if attrname == "content":
                content = value
        if name:
            self.metatags[ name ] = content

    def unknown_startag( self, tag, attrs ):
        self.setliteral()

    def unknown_endtag( self, tag ):
        self.setliteral()

#
#   HTML cleaning code
#

# These are the HTML tags that we will leave intact
VALID_TAGS = { 'a'          : 1
             , 'b'          : 1
             , 'base'       : 0
             , 'big'        : 1
             , 'blockquote' : 1
             , 'body'       : 1
             , 'br'         : 0
             , 'caption'    : 1
             , 'cite'       : 1
             , 'code'       : 1
             , 'dd'         : 1
             , 'del'        : 1
             , 'div'        : 1
             , 'dl'         : 1
             , 'dt'         : 1
             , 'em'         : 1
             , 'h1'         : 1
             , 'h2'         : 1
             , 'h3'         : 1
             , 'h4'         : 1
             , 'h5'         : 1
             , 'h6'         : 1
             , 'head'       : 1
             , 'hr'         : 0
             , 'html'       : 1
             , 'i'          : 1
             , 'ins'        : 1               
             , 'img'        : 0
             , 'kbd'        : 1
             , 'li'         : 1
           # , 'link'       : 1 type="script" hoses us
             , 'meta'       : 0
             , 'ol'         : 1
             , 'p'          : 1
             , 'pre'        : 1
             , 'small'      : 1
             , 'span'       : 1
             , 'strong'     : 1
             , 'sub'        : 1
             , 'sup'        : 1
             , 'table'      : 1
             , 'tbody'      : 1
             , 'td'         : 1
             , 'th'         : 1
             , 'title'      : 1
             , 'tr'         : 1
             , 'tt'         : 1
             , 'u'          : 1
             , 'ul'         : 1

             }

NASTY_TAGS = { 'script'     : 1
             , 'object'     : 1
             , 'embed'      : 1
             , 'applet'     : 1
             }


class StrippingParser( SGMLParser ):

    """ Pass only allowed tags;  raise exception for known-bad.
    """
    entitydefs = entitydefs

    def __init__( self, valid_tags=None, nasty_tags=None ):
        SGMLParser.__init__( self )
        self.result = ""
        self.valid_tags = valid_tags or VALID_TAGS
        self.nasty_tags = nasty_tags or NASTY_TAGS

    def handle_data( self, data ):
        if data:
            self.result = self.result + data

    def handle_charref( self, name ):
        self.result = "%s&#%s;" % ( self.result, name )

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''

        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones.
        """
        if self.valid_tags.has_key(tag):
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if k.lower().startswith('on'):
                    msg = _(u"JavaScript event '${attribute}' not allowed.",
                            mapping={'attribute': k})
                    raise IllegalHTML(msg)
                if v.lower().startswith('javascript:'):
                    msg = _(u"JavaScript URI '${value}' not allowed.",
                            mapping={'value': v})
                    raise IllegalHTML(msg)
                self.result = '%s %s="%s"' % (self.result, k, v)

            endTag = '</%s>' % tag
            if self.valid_tags.get(tag):
                self.result = self.result + '>'
            else:
                self.result = self.result + ' />'
        elif self.nasty_tags.get(tag):
            msg = _(u"Dynamic tag '${tag}' not allowed.",
                    mapping={'tag': tag})
            raise IllegalHTML(msg)
        else:
            pass    # omit tag

    def unknown_endtag(self, tag):
        if self.valid_tags.get(tag):
            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag




