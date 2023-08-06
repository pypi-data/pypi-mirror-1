from zope.interface import Interface
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import ListSequenceWidget
from zope.app.form import CustomWidgetFactory

from collective.portlet.filtersearch import FilterSearchMessageFactory as _

class IFilterTag(Interface):
    name = schema.TextLine(
        title=_(u"Criteria title"), 
        required=False
    )
    
    index_name = schema.TextLine(title=_(u"Main index"), required=False)
    value = schema.TextLine(title=_(u"Value"), required=False)

    show_unique = schema.Bool(title=_(u"Expand list with unique values"), required=False)

    metadata_name = schema.TextLine(title=_(u"Sub index"), required=False)


class FilterTag:
    implements(IFilterTag)
    def __init__(self, name=u"", index_name=u"", value=u"", metadata_name=u"", show_unique = False):
        self.name = name
        self.index_name = index_name
        self.metadata_name = metadata_name
        self.show_unique = show_unique
        self.value = value

class IFilterSearch(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    filter_tags = schema.List(
        title=_(u'Filter tags'),
        description=_(u'Filter tags that are shown in the portlet'),
        value_type=schema.Object(IFilterTag, title=_(u"Filter tag")),
        required=False)

filter_tag_widget = CustomWidgetFactory(ObjectWidget, FilterTag)
filter_tags_widget = CustomWidgetFactory(ListSequenceWidget, subwidget=filter_tag_widget)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFilterSearch)

    filter_tags = []
    def __init__(self, filter_tags=[]):
        self.filter_tags = filter_tags
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Filter search"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('filtersearch.pt')

    @property
    def available(self):
        # FIXME - how to do a general search availability check ?
        return self.request.getURL().endswith('search')

    def filter_list(self):
        catalog = getMultiAdapter( (self.context, self.request), name=u"plone_tools").catalog()
#        brains = catalog.searchResults(REQUEST=self.request)
        brains = self.context.queryCatalog(REQUEST = self.request)
        self.count = len(brains)
        filter_tags = self.data.filter_tags
        
        """
        This is not in use now, but leaving for later reference 
        
        filter_tags_indexes = []
        for tag in filter_tags:
            if tag.index_name:
                filter_tags_indexes.append(tag.index_name)
            if tag.metadata_name:
                filter_tags_indexes.append(tag.metadata_name)
                

        base_url = "%s?" % self.request.getURL()
        for raw_key,val in self.request.form.items():
            key = raw_key.split(':')[0]
            if key not in filter_tags_indexes:
                base_url += "%s=%s&" % (key, val)
        """
        base_url = "%s?" % self.request.getURL()
        for key,val in self.request.form.items():
            if isinstance(val, bool):
                base_url += "%s:boolean=True&" % key
            else:
                base_url += "%s=%s&" % (key, val)

        filters = {}
        for brain in brains:
            for tag in filter_tags:
                val = brain[tag.index_name]
                if str(val) == tag.value:
                    spec_url = base_url
                    if isinstance(val, bool):
                        if not (tag.index_name, True) in self.request.form.items():
                            spec_url = "%s%s:boolean=True" % (base_url, tag.index_name)
                    else:
                        if not (tag.index_name, tag.value) in self.request.form.items():
                            spec_url = "%s%s=%s" % (base_url, tag.index_name, tag.value)

                    if not filters.has_key(tag.name):
                        filters[tag.name] = {'title': tag.name,
                                             'url': spec_url,
                                             'count': 0,
                                             'uniques': {}}
                    filters[tag.name]['count'] += 1

                    if tag.show_unique:
                        metas = brain[tag.metadata_name]
                        if not metas:
                            continue
                            
                        if not isinstance(metas, list):
                            metas = [metas,]

                        for meta in metas:
                            meta_url = spec_url
                            if isinstance(meta, bool):
                                if not (tag.metadata_name, True) in self.request.form.items():
                                    meta_url = "&%s%s:boolean=True" % (spec_url, tag.metadata_name)
                            else:
                                if not (tag.metadata_name, meta) in self.request.form.items():
                                    meta_url = "%s&%s=%s" % (spec_url, tag.metadata_name, meta)

                            
                            if not filters[tag.name]['uniques'].has_key(meta):
                                filters[tag.name]['uniques'][meta] = {'title': meta,
                                                                      'url': meta_url,
                                                                      'count': 0}
                            filters[tag.name]['uniques'][meta]['count'] += 1
                        
        return filters.values()
        
# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFilterSearch)
    form_fields['filter_tags'].custom_widget = filter_tags_widget

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFilterSearch)
    form_fields['filter_tags'].custom_widget = filter_tags_widget
