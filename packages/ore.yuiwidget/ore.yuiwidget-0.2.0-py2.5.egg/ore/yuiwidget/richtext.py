##############################################################################
#
# Copyright (c) 2008 Kapil Thangavelu <kapil.foss@gmail.com>
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

from zope.app.form.browser.widget import UnicodeDisplayWidget
from zope.app.form.browser.textwidgets import TextAreaWidget
from zc.resourcelibrary import need

import xss

class HTMLDisplay( UnicodeDisplayWidget ):
    
    def __call__( self ):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""    
        return unicode(value)

class HTMLTextEditor( TextAreaWidget ):
    """
    a rich text editor using YUI's SimpleEditor
    """
    # text editor options
    height = '300px'
    width  = '500px'
    focus_start = 'false'
    dompath = 'false'
    markup = 'semantic' # (or css, default, xhtml)
    removeLineBreaks = 'false'
    extracss = ''
    
    def __call__( self ):
        # require yahoo rich text editor and dependencies
        need('yui-editor')
        
        # render default input widget for text
        input_widget = super( HTMLTextEditor, self).__call__()
        
        # use '_' instead of '.' for js identifiers
        jsid = self.name.replace('.','_')
        
        # attach behavior to default input widget, disable titlebar
        input_widget += u"""
        <script language="javascript">
            options={ height:'%s', 
                      width:'%s', 
                      dompath:%s, 
                      focusAtStart:%s,
                      removeLineBreaks:%s,
                      extracss=%s,
                      markup=%s};
            var %s_editor = new YAHOO.widget.SimpleEditor('%s', options); 
            YAHOO.util.Event.on(
                %s_editor.get('element').form, 
                'submit', 
                function( ev ) { 
                    %s_editor.saveHTML(); 
                    }
                );            
            %s_editor._defaultToolbar.titlebar = false;
            %s_editor.render();     
        </script>    
        """%(self.height,
             self.width,
             self.dompath,
             self.focus_start,
             self.removeLineBreaks,
             self.extracss,
             self.markup,
             jsid, self.name, jsid, jsid, jsid, jsid)
        
        # return the rendered input widget
        return input_widget
    
    def _toFieldValue( self, value ):
        return xss.filter( value )
            
