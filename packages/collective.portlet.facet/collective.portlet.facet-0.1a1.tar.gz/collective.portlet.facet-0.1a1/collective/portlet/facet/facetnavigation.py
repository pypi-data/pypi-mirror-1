from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr

from collective.facetsupport.interfaces import IFacetBuilder

from collective.portlet.facet import FacetNavigationMessageFactory as _

from ZTUtils import make_query

class IFacetNavigation(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    portlet_title = schema.TextLine(
        title = _(u"Title"),
        required=False,
        description=_(u"This is the title that the portlet will have if any"), 
    )

    facets = schema.Text(title=_(u"Facets to use"),
        description=_(u"Here you specify which facets you want to use. Facets must be a catalog index."),
        required=True,
    )
    
    view_template = schema.TextLine(title = _(u"View"),
        required=False,
        description=_(u"Specify the view template to be used here if different from the default view."), 
    )

    show_search = schema.Bool(title=_(u"Show search box on top?"),
        default = False,
        #description=_(u""),
    )

    show_zero = schema.Bool(title=_(u"Show terms that don't have any results?"),
        default = False,
        #description=_(u""),
    )
    
    clicking_again_deselects = schema.Bool(
        title=_(u"Clicking a selected facet deselects it?"),
        default = True,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    #For the 'manage portlets' screen.
    title = _(u'facet_navigation_portlet_title',
                default=u"Facet navigation portlet")

    implements(IFacetNavigation)

    portlet_title = u""
    facets = u""
    view_template = u""
    show_search = False
    show_zero = False
    clicking_again_deselects = True

    def __init__(self,
                 portlet_title=u"",
                 facets=u"",
                 view_template=u"",
                 show_search = False,
                 show_zero = False,
                 clicking_again_deselects = True):

        self.portlet_title = portlet_title
        self.facets = facets
        self.view_template = view_template
        self.show_search = show_search
        self.show_zero = show_zero
        self.clicking_again_deselects = clicking_again_deselects


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    #FIXME: Portlet takes stuff from all over. Should only be shown in collection-contexts!

    render = ViewPageTemplateFile('facetnavigation.pt')
    
    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)
        
        self.getFriendlyName = getToolByName(self.context, 'portal_atct').getFriendlyName
        
        fb = self.facet_builder = IFacetBuilder(context)
        self.title = data.portlet_title and data.portlet_title or data.title
        
        #The adapter returns None if no update of the request is needed.
        facets_to_use = [x.encode('utf8').strip() for x in data.facets.splitlines()]
        data = fb.facet_data(facets_to_use)
        if data is not None:
            request.facetsupport = data
        fb.add_weight_data(request.facetsupport['facets'])
        
        

    @property
    def facets(self):
        return self.request.facetsupport['facets']
    
    @property
    def query(self):
        return self.request.facetsupport['query']

    @property
    def link_base_url(self):
        url = self.context.absolute_url()
        if base + '/map' in self.request.getURL():
            base = base + '/map/'
        if self.data.view_template:
            url = url + '/' + self.data.view_template
        return url

    @property
    def clear_all_url(self):
        """ Clear all get-requests from url that has to do with the facets. Keep everything else.
        """
        #FIXME: Implement
        return self.context.absolute_url()

    @property
    def clear_facet_url(self, facet):
        """ Clear a specific facet from url. (I.e. deselect something)
        """
        #FIXME: Implement
        return self.context.absolute_url()

    def friendly_name(self, text):
        """ Fetch friendly name from portal_atct and then pass it to the translation machinery.
        """
        return _( self.getFriendlyName(text) )

    def normalize_css(self, text):
        return self.facet_builder.normalize_css(text)

    def link_for_term(self, facet, term):
        query = self.facet_builder.facet_query(**{facet:term})
        #If this term is selected and second click should remove, we need to remove the link
        if self.data.clicking_again_deselects:
            if facet in self.query and self.query[facet] == term:
                del query[facet]
        return "%s?%s" % (self.link_base_url, make_query(query))

    def query_link(self, remove=None):
        """ A link for a query. Remove keyword in remove.
        """
        query = self.query.copy()
        if remove in query:
            del query[remove]
        return make_query(query)

    def is_selected_term(self, facet, term):
        """ Check if term is selected.
        """
        if facet not in self.query:
            return False
        return self.query[facet] == term

#    @property
#    def clear_all_url(self):
#        """
#        """
#        
#        request_form = self.request.form.copy()
#        facets_to_remove = self._facets
#        if self.data.show_search and not self.data.is_search_portlet:
#            facets_to_remove.append(self._search_facet)
#
#        for index in facets_to_remove:
#            if request_form.has_key(index['id']):
#                del request_form[index['id']]
#        return self.root_url + "?" + make_query(request_form)
#
#   
#    @property 
#    def _facets(self):
#        """returns the configured facets
#        """
#        facets = []
#        for line in self.data.indexes.splitlines():
#            facet_split = line.split('|')
#            facet = {}
#            
#            if len(facet_split) == 3:
#                facet['id'] = facet_split[0]
#                facet['label'] = facet_split[1]
#                facet['property'] = facet_split[2]
#                
#            elif len(facet_split) == 2:
#                facet['id'] = facet_split[0]
#                facet['label'] = facet_split[1]
#            else:
#                facet['id'] = facet['label'] = facet_split[0]
#            
#            facet['id'] = urllib.quote_plus(facet['id'])
#            facets.append(facet)
#            
#        return facets 
#        
#    def _remove_batching_vars(self, request_form):
#        if request_form.has_key('b_start'):
#            del request_form['b_start']
#        return request_form
#    
#    def _remove_from_url(self, item):
#        """Take all previously selected and remove item 
#        """
#        dictionary = {}
#        
#        for selected in self._raw_selected():
#            dictionary[selected[0]] = selected[1]
#        
#        key = item[0]
#        value = item[1]
#        request_form = self.request.form.copy()
#        request_form = self._remove_batching_vars(request_form)
#        
#        if request_form.has_key(key):
#            del request_form[key]
#        
#        if key == 'SearchableText' and dictionary.has_key(key):
#            del dictionary[key]
#            
#        if dictionary.has_key(key):
#            dictionary[key].remove(value)
#                                
#        return self.root_url + "?" + make_query(request_form,dictionary)
#            
#    
#    def _add_to_url(self, item):
#        """Take all previously selected and add item 
#        """
#        dictionary = {}
#        request_form = self.request.form.copy()
#        request_form = self._remove_batching_vars(request_form)
#
#        for selected in self._raw_selected():
#            dictionary[selected[0]] = selected[1]
#        
#        key = item[0]
#        value = item[1]
#
#        itemlist = []
#        if request_form.has_key(key):
#            itemlist.extend(request_form[key])
#        itemlist.append(value)
#        dictionary[key] = itemlist
#                    
#        return self.root_url + "?" + make_query(request_form,dictionary)
#        
#    def _raw_selected(self):
#        """Returns a generator giving (id, value) tuples of the selected facets.
#        """
#        facets = self._facets
#        if self.data.show_search:
#            facets.append(self._search_facet)
#        
#        for facet in facets:
#            if self.request.has_key(facet['id']):
#                value = self.request.get(facet['id'])
#                
#                # this little thing is to break the memory reference to the same place. 
#                # Otherwise the changes in the returned list will show up in the "real" request.
#                if type(value) == type([]):
#                    value = value[:]
#                
#                yield (facet['id'], value)
#        
#    def get_selected_facets(self):
#        """a list of tuples dictionaries having this structure
#        
#            {'id': id, # this is the id
#             'label': label, # this is the label that is to be displayed
#             'values': [...] # this is a list of what is selected under this category.
#            }
#            
#            where 'values' is a list of dictionaries 
#            
#            {'id': id, # this is the id
#             'label': label, # this is the label that is to be displayed
#             'url': url, # this is the url for removing this option. ie all other selections minus this one.
#            }
#            
#        """
#        
#        
#        facets = self._facets
#        if self.data.show_search and not self.data.is_search_portlet:
#            facets.insert(0,self._search_facet)
#        
#        selected = []
#        for facet in facets:
#            if self.request.has_key(facet['id']):
#                value = self.request.get(facet['id'])
#                
#                # if the value is empty, don't keep it.
#                # for example an empty search string.
#                if not value:
#                    continue
#                
#                if type(value) != type([]):
#                    value = [value]
#                    
#                values = []
#                for item in value:
#                    values.append({'id': item,
#                                   'label': item,
#                                   'url': self._remove_from_url((facet['id'],item)),
#                                   })
#                    
#                    
#                selected.append({'id': facet['id'],
#                                 'label': facet['label'],
#                                 'values': values})
#        
#        return selected
#    
#    def get_facets(self):
#        """a list of all facets that is selectable with all of their options.
#
#            {'id': id, # this is the id
#             'label': label, # this is the label that is to be displayed
#             'values': {...} # this is a list of values that can be selected under this category.
#            }
#
#            where 'values' is a dictionary with the structure
#            
#            {value_id: {'label': label,
#                        'url': url,
#                        'count': count,
#                        'id': id,
#                        'icon': icon_url (optional)
#                        },
#            ...}
#                                
#        """
#        
#        for facet in self._facets:
#            
#            # now the information about the facet is done,
#            # lets make the list of values that we can choose from.
#            
#            facet['values'] = odict.odict()
#            shall_sort = True
#            
#            if facet.has_key('property') and hasattr(self.portal_properties, 'extensions_properties'):
#                uniqeValueIterator =  self.portal_properties.extensions_properties.getProperty(facet['property'], [])
#                shall_sort = False
#                
#            elif self.portal_catalog.Indexes.get(facet['id']):                
#                uniqeValueIterator = list(self.portal_catalog.uniqueValuesFor(facet['id']))
#                uniqeValueIterator.sort()
#                                    
#            else:
#                uniqeValueIterator = ['could not find as index']
#
#            for uniqeValue in uniqeValueIterator:
#                if uniqeValue:
#                    facet['values'][uniqeValue] =  {'label': uniqeValue,
#                                                    'count': 0,
#                                                    'id': urllib.quote_plus(uniqeValue)}
#
#                    selected_values = self.request.get(facet['id'], [])
#                    
#                    if uniqeValue == selected_values or uniqeValue in selected_values:
#                        facet['values'][uniqeValue]['url'] = self._remove_from_url((facet['id'],uniqeValue))
#                    else:
#                        facet['values'][uniqeValue]['url'] = self._add_to_url((facet['id'],uniqeValue))
#            
#            
#            facet_ids = [x['id'] for x in self._facets]
#            filterQuery = {}
#            request_form = self.request.form.copy()
#            for request_key in request_form:
#                if request_key in facet_ids:
#                    filterQuery[request_key] = {'query': request_form[request_key],
#                                                'operator': 'and'}
#            
#            if self.data.default_query:
#                filterQuery.update(eval(self.data.default_query))
#            
#            if self.data.show_search and request_form.has_key(self._search_facet['id']):
#                filterQuery[self._search_facet['id']] = request_form[self._search_facet['id']]
#
#                
#            
#            if self.data.is_search_portlet or self.root.meta_type == 'ATTopic':
#                use_types_blacklist=self.request.get('use_types_blacklist', True)
#                use_navigation_root=self.request.get('use_navigation_root', True)
#                content = self.root.queryCatalog(REQUEST=filterQuery,use_types_blacklist=use_types_blacklist, use_navigation_root=use_navigation_root)
#            else:
#                content = self.root.getFolderContents(contentFilter = filterQuery)
#                
#            # iterate over the unique values in this context.
#            for item in content:
#                # check if the item has a value for the appropriate index
#                value = getattr(item, facet['id'], None)
#                if callable(value):
#                    value = value()
#                    
#                if value:
#                    if type(value) == str:
#                        value = [value]
#
#                    for single_value in value:
#                        if facet['values'].has_key(single_value):
#                            # it is already there, just increase the count by one
#                            facet['values'][single_value]['count'] += 1
#
#            
#            values_list = [x for x in facet['values'].values() if x['count'] > 0]
#            
#            if shall_sort:
#                values_list.sort(lambda x, y: cmp(x['label'], y['label']))
#                
#            facet['values'] = values_list
#            yield facet
                        


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFacetNavigation)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFacetNavigation)
