from tw.api import Widget, CSSLink, lazystring as _

from rum import app
from rum.genericfunctions import generic

 

class ContextLinks(Widget):
    def _resource_name(self, routes):
         r_names, r_namep = app.names_for_resource(routes['resource'])
         return  app.translator.ugettext(r_names)
    @generic
    def gen_links(self, routes):
        pass
    @gen_links.when()
    def _gen_links_default(self, routes):
        return []
    def std_link_tuple(self, name, resource_action=True):
        new_name=name[:1].upper()+name[1:]
        args=dict(action=name)
        if resource_action:
            args['id']=None
        return (name, _(new_name), app.url_for(**args))
    def index_link_tuple(self):
        # return ('index',
        #              _('Index'),
        #              app.url_for(action='index'))
        return self.std_link_tuple("index")
    def edit_link_tuple(self):
        return self.std_link_tuple("edit", resource_action=False)
    def show_link_tuple(self):
        return self.std_link_tuple("show", resource_action=False)
    def new_link_tuple(self):
        routes=app.request.routes
        return ('new',
        _(u'Create a new %(resource_name)s') % dict(resource_name=self._resource_name(routes)),
            app.url_for(action='new'))
    @gen_links.when("routes['resource'] is not None")
    def _gen_links_res(self, routes):
        return [self.index_link_tuple(),
                self.new_link_tuple()]
    
    def delete_link_tuple(self):
        return ('confirm_delete', _('Delete'), app.url_for(action='delete'))
    
    @gen_links.when("routes['resource'] is not None and routes.get('id',None) is not None")
    def _gen_links_obj(self, routes):
        return [
                self.edit_link_tuple(),
                self.show_link_tuple(),
                self.index_link_tuple(),
                self.new_link_tuple(),
                self.delete_link_tuple()
                ]
    
    def update_params(self, d):
        super(ContextLinks, self).update_params(d)
        current_action=app.request.routes['action']
        d.links=[(titel, link) 
            for (action, titel, link) in 
            self.gen_links(app.request.routes) 
            if action!=current_action]
    template="genshi:tw.rum.templates.context_links"
    css=[CSSLink(modname="tw.rum", filename='static/context_links.css')]