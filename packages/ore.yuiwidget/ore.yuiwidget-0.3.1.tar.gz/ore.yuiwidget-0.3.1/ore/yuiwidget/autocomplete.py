"""
Autocomplete widgets

  ISourceQueryable
  SourceQueryView
  
  SourceQueryJSON

  Site Source AutoCompletes

  Context Source Auto Completes

    
$Id: $
"""

from zope.app.form.browser import itemswidgets, textwidgets, interfaces



from zope import interface
from zc.resourcelibrary import need
from ore.alchemist import model, Session

import simplejson

class AutoComplete( object ):

    source = None


class SiteSourceQueryView( object ):

    interface.implements( interfaces.ISourceQueryView )

    template = """
    <div id="%(name)s.autofield">
       <input id="%(name)s" type="text">
       <div id="%(name)s.autodiv">
       </div>
    </div>
    
    <script type="text/javascript">
      
      search_schema = var mySchema2 = ["ResultItem", "KeyDataField"];
      data_source = new YAHOO.widget.DS_XHR("%(source_url)s", search_schema; 
    </script>
    """

    # source views should be registered on a site
    source_view = ""

    columns = None
    # do not mutate at runtime
    config = {}
    
    def render( self, name):
        need("yui-autocomplete")
        ns = {}
        ns.update( self.config )
        ns['search_url'] = self.search_url
        ns['name'] = self.name + '.searchstring'
        return self.template%(ns)

    @property
    def item_field_mapping( self ):
        domain_interface = model.queryModelInterface( self.context.domain_model )
        schema.getFields( domain_interface )
        
        
    @property
    def search_url( self ):
        #site = getSite()
        #site_url = absoluteURL( site, self.request )
        url = absoluteURL( self.context, self.request )
        return url + self.search_view
    
    def results( self ):
        # results are delegated to the queryjson view
        return []

class SourceQueryJSON( object ):
    """a view providing json (results) of querying sources
    """
    
    def __init__( self, context, request ):
        self.context = context
        self.request = request
        self.queryable = ISourceQuery( context )

    def __call__( self ):
        query_term = self.request.get('query')
        if not query_term:
            return simplejson.dumps( [] )
        results = self.queryable.query( query_term )
        return simplejson.dumps( [] )

class TextColumnSourceQuery( object ):

    interface.implements( interfaces.ISourceQuery )
    
    def __init__( self, context, column_name ):
        self.context
        self.column_name = column_name

    def query( self, term):
        domain_model = self.context.domain_model
        results = Session().query(domain_model).filter(
            domain_model.c[self.column_name].like(
                '\%s%s\%'%term
                ).all()
            )
        return results

class ISourceQuery( interface.Interface ):

    def query( search_term ):
        """
        query a source for a search term
        """

    def hasTerm( term ):
        """
        verify the existence of a term
        """
    

