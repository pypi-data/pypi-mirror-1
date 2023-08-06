from genshi.input import HTML
from tw import framework
from tw.api import Link, CSSLink
from tw.forms import DataGrid
from tw.forms.datagrid import Column
from rum import app
from rum.query import asc, desc
modname = "tw.rum"

class RumDataGrid(DataGrid):
    css_class = "rum-grid"
    css = [CSSLink(modname=modname, filename="static/grid.css")]
    actions = ["show", "edit", "confirm_delete"]
    params = ["actions", "icons", "query"]
    icons = {
        'edit': Link(modname=modname, filename="static/pencil.png"),
        'show': Link(modname=modname, filename="static/pencil_go.png"),
        'confirm_delete': Link(modname=modname,
                               filename="static/pencil_delete.png"),
        }
    template="tw.rum.templates.datagrid"
    def __init__(self, *args, **kw):
        super(RumDataGrid, self).__init__(*args, **kw)
        self.fields.insert(0, (' ', self.row_links))

    def row_links(self, row):
        tpl = u'<a class="rum-grid-action" href="%(url)s" title="%(title)s">'\
              u'<img alt="%(title)s" src="%(src)s" /></a>'
        return HTML('<span class="rum-grid-action">' +''.join(tpl % {
            'url': app.url_for(obj=row, action=action),
            'src': self.icons[action].link,
            'title': framework.translator(action),
            } for action in self.actions) +"</span>")



        
    def update_params(self, d):
        super(RumDataGrid, self).update_params(d)
        query = d.query
        
        def css_for_column_header(i, col):
            res=["col_"+str(i)]
            if query.sort:
                first=query.sort[0]
                if first==asc(col.name):
                    res.append("rum-data-grid-asc")
                else:
                    if first==desc(col.name):
                        res.append("rum-data-grid-desc")
            return " ".join(res)
        def link_for_sort_key(sort_key):
            if query.sort:
                old_sort=[c for c in query.sort if not c in [asc(sort_key),desc(sort_key)]]
            else:
                old_sort=[]
            prepend=asc(sort_key)
            if query.sort and query.sort[0]==asc(sort_key):
                prepend=desc(sort_key)
            new_sort=[prepend]+old_sort
            new_query = query.clone(sort=new_sort)

            return app.url_for(**new_query.as_flat_dict())
        def sortable_column(col):
            return "field" in col.options and getattr(col.options["field"], "sortable", False)
        d.link_for_sort_key = link_for_sort_key
        d.css_for_column_header=css_for_column_header
        d.sortable_column=sortable_column