"""
$Id: $
"""

from zc.table import table
from zc.resourcelibrary import need
from zope.traversing.browser import absoluteURL

table_js_template ="""
<script type="text/javascript">
    YAHOO.util.Event.onDOMReady(function(){
  
    var datasource, columns, config

    // Setup Datasource for Container Viewlet
    datasource = new YAHOO.util.DataSource("%(data_url)s");
    datasource.responseType   = YAHOO.util.DataSource.TYPE_JSON;
    datasource.responseSchema = {
      resultsList: "nodes",
      fields: [ %(fields)s ],
      metaFields: { totalRecords: "length", sortKey:"sort", sortDir:"dir", paginationRecordOffset:"start"}
      }
      
    columns = [ %(columns)s ];
    
    // A custom function to translate the js paging request into a datasource query 
    var buildQueryString = function (state,dt) {
        sDir = (dt.get("sortedBy").dir === "asc"||dt.get("sortedBy").dir == "") ? "" : "desc";
        var query_url = "start=" + state.pagination.recordOffset + "&limit=" + state.pagination.rowsPerPage + "&sort=" + dt.get("sortedBy").key  + "&dir="+sDir;
        return query_url
    };
    
    config = {
       paginator : %(paginator)s,
       initialRequest : 'start=0&limit=20',
       generateRequest : buildQueryString,
       paginationEventHandler : YAHOO.widget.DataTable.handleDataSourcePagination,
       %(js_default_sort)s,
       %(js_config)s
    }

    table = new YAHOO.widget.DataTable( YAHOO.util.Dom.get("%(table_id)s"), columns, datasource, config  )    
    table.sortColumn = function(oColumn) {
        // Default ascending
        var sDir = "asc";
        
        // If already sorted, sort in opposite direction
        if(oColumn.key === this.get("sortedBy").key) {
           sDir = (this.get("sortedBy").dir === "asc"||this.get("sortedBy").dir == "") ? "desc" : "asc";
           }

        // Pass in sort values to server request
        var newRequest = "sort=" + oColumn.key + "&dir=" + sDir + "&start=0";
        // Create callback for data request
        var oCallback = {
                success: this.onDataReturnInitializeTable,
                failure: this.onDataReturnInitializeTable,
                scope: this,
                argument: {
                    // Pass in sort values so UI can be updated in callback function
                    sorting: {
                        key: oColumn.key,
                        dir: (sDir === "asc") ? YAHOO.widget.DataTable.CLASS_ASC : YAHOO.widget.DataTable.CLASS_DESC
                    }
                }
            }
            
        // Send the request
        this.getDataSource().sendRequest(newRequest, oCallback);
        
        };
        
    table.subscribe("rowMouseoverEvent", table.onEventHighlightRow); 
    table.subscribe("rowMouseoutEvent", table.onEventUnhighlightRow);
    %(js_extra)s
});
</script>
"""

        
class BaseDataTableFormatter( table.Formatter ):

    data_view ="/@@json"
    prefix = ""
    paginator = "new YAHOO.widget.Paginator({ rowsPerPage : 20 })"
    js_extra = ""
    js_config = ""
    js_default_sort = ""
    
    def __init__( self, context, request, items,  paginator=None, data_view=None, *args, **kw ):
        super( BaseDataTableFormatter, self).__init__( context, request, items, *args, **kw )
        if paginator:
            self.paginator = paginator
        if data_view:
            self.data_view = data_view
    
    def renderExtra( self ):
        need('yui-datatable')
        extra = table_js_template%(self.getDataTableConfig())
        return extra

    def getFields( self ):
        """ return zope.schema fields that should be displayed """
        raise NotImplemented
    
    def getDataTableConfig( self ):
        """
        fields
        columns
        table_id
        """
        config = {}
        config['columns'], config['fields'] = self.getFieldColumns()
        config['data_url'] = self.getDataSourceURL()
        config['table_id'] = self.prefix
        config['paginator'] = self.paginator
        config['js_extra'] = self.js_extra
        config['js_config'] = self.js_config
        config['js_default_sort'] = self.js_default_sort or \
                    'sortedBy : { key: "na", dir : "asc" }'
        
        #config['sort_field'] = self.columns[0].name.replace(' ', '_').lower()
        return config

    def __call__(self):
        return '<div id="%s">\n<table %s>\n%s</table>\n%s</div>' % (
                self.prefix,
                self._getCSSClass('table'), self.renderContents(),
                self.renderExtra())
    
    def getFieldColumns( self ):
        # get config for data table
        column_model = []
        field_model  = []

        for field in self.getFields( ):
            key = field.__name__
            column_model.append(
                '{key:"%s", label:"%s", sortable:true}'%( key, field.title )
                )
            field_model.append(
                '{key:"%s"}'%( key )               
                )
        #columns, fields
        return ','.join( column_model ), ','.join( field_model )

    def getDataSourceURL( self ):
        url = absoluteURL( self.context, self.request )
        url += ( self.data_view + '?')
        return url

class ContainerDataTableFormatter( BaseDataTableFormatter ):
    data_view ="/@@json"
    prefix = 'datacontents_id'

    def getFields( self ):
        import alchemist.ui.container
        return alchemist.ui.container.getFields( self.context )
    
class ContextDataTableFormatter( BaseDataTableFormatter ):
    pass

        
