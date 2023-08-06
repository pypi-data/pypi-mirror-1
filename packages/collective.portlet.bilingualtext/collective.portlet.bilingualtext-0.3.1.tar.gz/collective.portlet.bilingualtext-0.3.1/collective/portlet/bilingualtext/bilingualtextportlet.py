from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.bilingualtext import PloneMessageFactory as _
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

languages = ('DE', 'EN', 'FR')

class IBilingualTextPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    lang = schema.Choice(languages,
        title=_(u"Language"),
        description=_(u"Language"),
        default='DE',
        required=True)

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    text = schema.Text(
        title=_(u"Text"),
        description=_(u"Text"),
        required=True)

    footer = schema.TextLine(
        title=_(u"Portlet footer"),
        description=_(u"Text to be shown in the footer"),
        required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBilingualTextPortlet)

    lang = u''
    header = u''
    text = u''
    footer = u''

    def __init__(self, header=u'', lang=u'', text=u'', footer=u''):
        self.header = header
        self.lang = lang
        self.text = text
        self.footer = footer

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Multilingual text portlet (%s)" % self.lang

    def isAvailable(self, context):
        """ Check if portlet must be displayed for this language """
        current_language = context.REQUEST.get('LANGUAGE', 'en').lower()
        return current_language.startswith(self.lang.lower())


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('bilingualtextportlet.pt')


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IBilingualTextPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    label = _(u"title_add_static_portlet",
              default=u"Add language dependent text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text (language dependent).")


    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IBilingualTextPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    label = _(u"title_add_static_portlet",
              default=u"Edit language dependent text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text language-dependent.")
