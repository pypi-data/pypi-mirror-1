from urllib import quote, quote_plus
from string import Template
from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quintagroup.portlet.generichtml import GenericHTMLPortletMessageFactory as _

DEFAULT_CONTENT = "Here can be your content"

class IGenericHTMLPortlet(IPortletDataProvider):

    content = schema.Text( title=_(u'Generic HTML Portlet content'),
                           description=_(u"content_field_description", default=u"""\
Enter your html code here. Please use '$categories', '$enc_categories' or '$encplus_categories' 
variables to use categories from current context in your code.
For example: $categories will be substituted for 'some category1,some category2', 
$enc_categories will be substituted for 'some%20category1%2Csome%20category2', 
$encplus_categories will be substituted for 'some+category1%2Csome+category2',
where some category1, some category2 are categories of your current content."""),
                           required=True
                         )


class Assignment(base.Assignment):
    implements(IGenericHTMLPortlet)

    def __init__(self, content=DEFAULT_CONTENT):
        self.content = content

    @property
    def title(self):
        return _(u"Generic HTML Portlet")

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('generichtmlportlet.pt')

    def render(self):
        return xhtml_compress(self._template())

    def ptcontent(self):
        content = Template(self._data())
        return content.substitute( **self.context_categories())

    def context_categories( self ):
        categories = self.context.Subject() 
        return {'categories':','.join(categories),
                'enc_categories':quote(','.join(categories)),
                'encplus_categories':quote_plus(','.join(categories))}

    @memoize
    def _data(self):
        return self.data.content

class AddForm(base.AddForm):
    form_fields = form.Fields(IGenericHTMLPortlet)
    label = _(u"Add Generic HTML Portlet")
    description = _(u"This portlet displays html content.")

    def create(self, data):
        return Assignment(content=data.get('content', DEFAULT_CONTENT))

class EditForm(base.EditForm):
    form_fields = form.Fields(IGenericHTMLPortlet)
    label = _(u"Edit Generic HTML Portlet")
    description = _(u"This portlet displays html content.")
