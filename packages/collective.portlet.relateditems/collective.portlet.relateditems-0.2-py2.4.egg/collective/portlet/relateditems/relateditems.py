from ZTUtils import make_query

from zope.interface import implements
from zope.interface import providedBy
from Products.ATContentTypes.interface import IATTopic

from zope import schema
from zope.formlib import form
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.portlets.cache import render_cachekey
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.relateditems import RelatedItemsMessageFactory as _

# TODO: Folderish get categories from children

DEFAULT_ALLOWED_TYPES = (
    'News Item',
    'Document',
    'Event',
    'File',
    'Image',
)

class IRelatedItems(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    count = schema.Int(
        title=_(u'Number of related items to display'),
        description=_(u'How many related items to list.'),
        required=True,
        default=10
    )

    states = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=('published', ),
        required=True,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates"
        )
    )

    allowed_types = schema.Tuple(
        title=_(u"Allowed Types"),
        description=_(u"Select the content types that should be shown."),
        default=DEFAULT_ALLOWED_TYPES,
        required=True,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"
        )
    )
    
    show_all_types = schema.Bool(
        title=_(u"Show all types in 'more' link"),
        description=_(u"If selected, the 'more' link will display "
                       "results from all content types instead of "
                       "restricting to the 'Allowed Types'."),
        default=False,
    )

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRelatedItems)

    def __init__(self, 
                 count=5,
                 states=('published',),
                 allowed_types=DEFAULT_ALLOWED_TYPES,
                 show_all_types=False):
        self.count = count
        self.states = states
        self.allowed_types = allowed_types
        self.show_all_types = show_all_types

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Related Items"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    _template = ViewPageTemplateFile('relateditems.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self._data())

    def getRelatedItems(self):
        return self._data()

    @property
    def showRelatedItemsLink(self):
        """Determine if the 'more...' link needs to be displayed
        """
        # if the more link is for all types then always show it
        if self.data.show_all_types:
            return True
        # if we have more results than are shown, show the more link
        elif len(self.all_results) > self.data.count:
            return True
        return False

    def getAllRelatedItemsLink(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal_url = portal_state.portal_url()        
        context = aq_inner(self.context)
        req_items = {}
        # make_query renders tuples literally, so let's make it a list
        req_items['Subject'] = list(context.Subject())
        if not self.data.show_all_types:
            req_items['portal_type'] = list(self.data.allowed_types)
        return '%s/search?%s' % (portal_url, make_query(req_items))

    
    def _contents(self):
        contents = []
        # Collection
        if IATTopic.providedBy(self.context):
            contents = self.context.queryCatalog(sort_limit=5)
        # probably a folder
        else:
            contents = self.context.getFolderContents()
              
        return contents    
 
    def _itemQuery(self, value):
        search_query = []

        # Include categories in the search query
        # Transformed to lowercase to not disrupt search (AND,OR,etc)
        keywords = map(lambda x: x.lower(), value.Subject())

        # Include words from title in the search query
        # Transformed to lowercase to not disrupt search (AND,OR,etc) 
        title = value.Title().lower().split()
        
        search_query = title + keywords
        return search_query

    def _itemsQuery(self, values):
        query = ''
        items = []
        for item in values:
            items += self._itemQuery(item)
        
        # remove duplicated search keywords
        items = self.uniq(items)
                  
        query = items.pop(0)
        for item in items:
            query += ' OR ' + item
                        
        return query

    def uniq(self, alist):    # Fastest order preserving
        set = {}
        return [set.setdefault(e,e) for e in alist if e not in set]

    def _query(self):    
        keywords = []        
        context = aq_inner(self.context)
        
        # TODO: test if a collection limited to 3 items show anything...
        # get items in folder or collection
        contents = []
        if self.context.isPrincipiaFolderish:
            contents = self._contents()
            contents = map(lambda x: x.getObject(), contents)     
                
        contents.insert(0,self.context);
        
        search_query = self._itemsQuery(contents)
        return search_query
            
    @memoize
    def _data(self):
        plone_tools = getMultiAdapter((self.context, self.request),
                                      name=u'plone_tools')
        context = aq_inner(self.context)
        keywords = context.Subject()
        here_path = ('/').join(context.getPhysicalPath())
        
        # Exclude items from related if contained in folderish
        content = []
        if self.context.isPrincipiaFolderish:
            content = self._contents()
        exclude_items = map(lambda x: x.getPath(), content)
              
        exclude_items += [here_path]
        #print exclude_items
        #exclude_items = [here_path]       
        
        catalog = plone_tools.catalog()
        limit = self.data.count
        # increase by one since we'll get the current item
        extra_limit = limit + len(exclude_items)
        
        search_query = self._query()
        #print 'search_query = '+search_query  
                
        results = catalog(portal_type=self.data.allowed_types,
                          #Subject=keywords,
                          SearchableText= search_query,
                          review_state=self.data.states,
                          #sort_on='Date',
                          #sort_order='reverse',
                          sort_limit=extra_limit)
        # filter out the current item
        self.all_results = [res for res in results if not res.getPath() in exclude_items]
        return self.all_results[:limit]

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRelatedItems)
    label = _(u"Add Related Items Portlet")
    description = _(u"This portlet displays recent Related Items.")

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          states=data.get('states', ('published',)),
                          allowed_types=data.get('allowed_types', 
                                                DEFAULT_ALLOWED_TYPES),
                          show_all_types=data.get('show_all_types', False))

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRelatedItems)
    label = _(u"Edit Related Items Portlet")
    description = _(u"This portlet displays recent Related Items based on "
                     "keywords matches.")
