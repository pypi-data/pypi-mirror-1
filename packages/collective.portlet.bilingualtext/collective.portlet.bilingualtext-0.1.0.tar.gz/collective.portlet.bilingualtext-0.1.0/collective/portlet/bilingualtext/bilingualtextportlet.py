from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.bilingualtext import BilingualTextPortletMessageFactory as _
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget


class IBilingualTextPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    text_en = schema.Text(
        title=_(u"English text"),
        description=_(u"English text"),
        required=True)

    text_de = schema.Text(
        title=_(u"German text"),
        description=_(u"German text"),
        required=True)

    footer = schema.TextLine(
        title=_(u"Portlet footer"),
        description=_(u"Footer of the rendered portlet"),
        required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBilingualTextPortlet)

    header = u''
    text_en = u''
    text_de = u''
    footer = u''

    def __init__(self, header=u'', text_en=u'', text_de=u'', footer=u''):
        self.header = header
        self.text_en = text_en
        self.text_de = text_de
        self.footer = footer 

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Bilingual text portlet"


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
    form_fields['text_en'].custom_widget = WYSIWYGWidget
    form_fields['text_de'].custom_widget = WYSIWYGWidget
    label = _(u"title_add_static_portlet",
              default=u"Add static text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text.")


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
    form_fields['text_en'].custom_widget = WYSIWYGWidget
    form_fields['text_de'].custom_widget = WYSIWYGWidget
    label = _(u"title_add_static_portlet",
              default=u"Add static text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text.")
