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

from zope.app.form.browser.textwidgets import DateWidget
from zc.resourcelibrary import need
from datetime import datetime, timedelta


class CalendarWidget( DateWidget ):

    # 4 year spread from server start by default
    mindate = (datetime.now()-timedelta( 365*2 )).strftime('%m/%d/%Y')
    maxdate = (datetime.now()+timedelta( 365*2 )).strftime('%m/%d/%Y')
    
    def getInputValue( self ):
        return super( CalendarWidget, self).getInputValue()

    def __call__( self ):
        need("yui-calendar")
        need("yui-container")
        need("yui-button")
        
        jsid = self.name.replace('.','_')
        value = self._getFormValue()
        
        if value is None or value == self.context.missing_value:
            value = ''
            
        input_widget = """\
        
        <div class="datefield">
           <input id="%(name)s" name="%(name)s" type="text" value="%(value)s"/>
           <button type="button" id="%(name)s-btn" title="Show Calendar"/>
              <img src="/++resource++calbtn.gif" />
            </button>
        </div>
        
        <div id="%(name)s-container">
           <div class="hd">Calendar</div>
           <div class="bd">
              <div id="%(name)s-caldiv"></div>
           </div>
        </div>
        
        <script language="javascript">
           YAHOO.util.Event.onDOMReady(function(){
           var dialog, calendar;
           var curdate = "%(value)s";
           
           pad = function (value, length) {
              value = String(value);
              length = parseInt(length) || 2;
              while (value.length < length)
                  value = "0" + value;
                  return value;
           };
           
           calendar = new YAHOO.widget.Calendar("%(name)s-caldiv", {
                    iframe:false,          // Turn iframe off, since container has iframe support.
                    hide_blank_weeks:true,  // Enable, to demonstrate how we handle changing height, using changeContent
                    mindate:"%(mindate)s",
                    maxdate:"%(maxdate)s",
                    navigator:true
                    });
           
            function handle_cancel() {
                this.hide();
            }

            function handle_ok() {
                if ( calendar.getSelectedDates().length > 0) {
                     var selDate = calendar.getSelectedDates()[0];
                     var datestring = selDate.getFullYear() + "-" + pad( selDate.getMonth()+1, 2) + "-" + pad( selDate.getDate(), 2);
                     document.getElementById("%(name)s").value = datestring;
                };
                this.hide();
            }

            dialog = new YAHOO.widget.Dialog("%(name)s-container", {
                  context:["%(name)s-btn", "tl", "bl"],
                  buttons:[ {text:"Select", isDefault:true, handler: handle_ok },
                            {text:"Cancel", handler: handle_cancel}],
                  width:"16em",  // Sam Skin dialog needs to have a width defined (7*2em + 2*1em = 16em).
                  draggable:false,
                  close:true
                  });        


            // calendar.select( "%(value)s" );
            calendar.render();
            dialog.render();
            
            // Using dialog.hide() instead of visible:false is a workaround for an IE6/7 container known issue with border-collapse:collapse.
            dialog.hide();
            
            calendar.renderEvent.subscribe(function() {
               dialog.fireEvent("changeContent");
               });
            YAHOO.util.Event.on("%(name)s-btn", "click", dialog.show, dialog, true);
            });
        </script>
        """%{ 'name' : self.name, 'value':value, 'mindate':self.mindate, 'maxdate':self.maxdate }
               
        
        return input_widget
