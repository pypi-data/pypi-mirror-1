from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.bilingualtext import BilingualTextPortletMessageFactory as _
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget


languages = ('DE', 'EN', 'FR')


class IBilingualTextPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    lang_1 = schema.Choice(languages,
        title=_(u"Language 1"),
        description=_(u"language 1"),
        default='DE',
        required=True)

    header_1 = schema.TextLine(
        title=_(u"Portlet header (language 1)"),
        description=_(u"Title of the rendered portlet (language 1)"),
        required=True)

    text_1 = schema.Text(
        title=_(u"Text language 1"),
        description=_(u"Text language 1"),
        required=True)

    lang_2 = schema.Choice(languages,
        title=_(u"Language 2"),
        description=_(u"language 2"),
        default='EN',
        required=False)

    header_2 = schema.TextLine(
        title=_(u"Portlet header (language 2)"),
        description=_(u"Title of the rendered portlet (language 2)"),
        required=True)

    text_2 = schema.Text(
        title=_(u"Text language 2"),
        description=_(u"Text language 2"),
        required=False)

    lang_3 = schema.Choice(languages,
        title=_(u"Language 3"),
        description=_(u"language 3"),
        default='FR',
        required=False)

    header_3 = schema.TextLine(
        title=_(u"Portlet header (language 3)"),
        description=_(u"Title of the rendered portlet (language 3)"),
        required=True)

    text_3 = schema.Text(
        title=_(u"Text language 3"),
        description=_(u"Text language 3"),
        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBilingualTextPortlet)

    header_1 = u''
    header_2 = u''
    header_3 = u''
    lang_1 = u''
    lang_2 = u''
    lang_3 = u''
    text_1 = u''
    text_2 = u''
    text_3 = u''
    footer = u''

    def __init__(self, header_1=u'',  header_2=u'', header_3=u'',
                 lang_1=u'', lang_2=u'', lang_3=u'',
                 text_1=u'', text_2=u'', text_3=u'', footer=u''):
        self.header_1 = header_1
        self.header_2 = header_2
        self.header_3 = header_3
        self.lang_1 = lang_1
        self.lang_2 = lang_2
        self.lang_3 = lang_3
        self.text_1 = text_1
        self.text_2 = text_2
        self.text_3 = text_3
        self.footer = footer 

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Bilingual text portlet"

    def getCurrentText(self, context):
        """ Return text 1-3 based on the current language """

        current_language = context.REQUEST.get('LANGUAGE', 'en')

        for i in range(1, 4):
            text = getattr(self, 'text_%d' % i)
            language = getattr(self, 'lang_%d' % i).lower()
            if text and current_language.lower().startswith(language):
                return text
        return u''


    def getCurrentHeader(self, context):
        """ Return header 1-3 based on the current language """

        current_language = context.REQUEST.get('LANGUAGE', 'en')

        for i in range(1, 4):
            header = getattr(self, 'header_%d' % i)
            language = getattr(self, 'lang_%d' % i).lower()
            if header and current_language.lower().startswith(language):
                return header
        return u''


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
    form_fields['text_1'].custom_widget = WYSIWYGWidget
    form_fields['text_2'].custom_widget = WYSIWYGWidget
    form_fields['text_3'].custom_widget = WYSIWYGWidget
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
    form_fields['text_1'].custom_widget = WYSIWYGWidget
    form_fields['text_2'].custom_widget = WYSIWYGWidget
    form_fields['text_3'].custom_widget = WYSIWYGWidget
    label = _(u"title_add_static_portlet",
              default=u"Add static text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text.")
