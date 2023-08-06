import re

from zope.interface import Interface

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema


from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.adsense import AdSensePortletMessageFactory as _

color_validator = re.compile("[a-fA-F\d]{6,6}$").match

class IAdSensePortlet(IPortletDataProvider):
    """A Google AdSense portlet"""

    ad_client = schema.TextLine(
        title=_(u"AdSense code"),
        description=_(u"Fill with your personal Google AdSense code"),
        required=True)

    ad_test = schema.Bool(
        title=_(u"Test mode"),
        description=_(u"Check this option to set test mode ON. Test mode should prevent clicks and impressions to be sent to Google while testing a website or the portlet itself. This is an undocumented option of AdSense."),
        default=True)

    ad_size = schema.Choice(
        title=_(u"Size"),
        description=_(u"Choose from available Ad formats"),
        vocabulary = 'AdSense.AdUnitSizesVocabulary' )

    ad_slot = schema.TextLine(
        title=_(u"Slot"),
        description=_(u"Paste your slot code here (numbers only). The size option of the portlet and the slot size must match "),
        required = False,
        constraint=re.compile("\d{10,10}$").match)

    color_border = schema.TextLine(
        title=_(u"Border color"),
        description=_(u"Choose a custom border color. Use hex color codes."),
        required=False,
        constraint=color_validator)

    color_bg = schema.TextLine(
        title=_(u"Background color"),
        description=_(u"Choose a custom background color. Use hex color codes."),
        required=False,
        constraint=color_validator)

    color_link = schema.TextLine(
        title=_(u"Link color"),
        description=_(u"Choose a custom link color. Use hex color codes."),
        required=False,
        constraint=color_validator)

    color_text = schema.TextLine(
        title=_(u"Text color"),
        description=_(u"Choose a custom text color. Use hex color codes."),
        required=False,
        constraint=color_validator)

    color_url = schema.TextLine(
        title=_(u"Url color"),
        description=_(u"Choose a custom URL color. Use hex color codes."),
        required=False,
        constraint=color_validator)

    alternate_color = schema.TextLine(
        title=_(u"Alternate color"),
        description=_(u"Choose a custom color for public server ads (PSA). Use hex color codes."),
        required=False,
        constraint=color_validator)

    color_text = schema.TextLine(
        title=_(u"Alternate URL"),
        description=_(u"Insert a custom URL to replace public server ads (PSA) with alternate ads."),
        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IAdSensePortlet)

    def __init__(self, ad_client=u"", ad_test=True, ad_size=(125,125),
                 ad_slot=None, color_bg = None, alternate_color = None,
                 color_border = None, color_link = None, color_url = None,
                 color_text = None, alternate_ad_url = None):

        self.ad_client = ad_client
        self.ad_test = ad_test
        self.ad_size = ad_size
        self.ad_slot = ad_slot
        self.color_bg = color_bg
        self.alternate_color = alternate_color
        self.color_border = color_border
        self.color_link = color_link
        self.color_url = color_url
        self.color_text = color_text
        self.alternate_ad_url = alternate_ad_url

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet AdSense"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('adsenseportlet.pt')

    @property
    def js_settings(self):
        data = self.data
        out =  []

        out.append('<!--')

        out.append('google_ad_client = "%s";' %data.ad_client)
        out.append('google_ad_width = %s;' %data.ad_size[0])
        out.append('google_ad_height = %s;' %data.ad_size[1])

        if data.ad_test:
            out.append('google_adtest = "on";')
        else:
            out.append('google_adtest = "off";')

        if data.ad_slot:
            out.append('google_ad_slot = "%s";' %data.ad_slot)

        if data.color_bg:
            out.append('google_color_bg = "%s";' %data.color_bg)

        if data.alternate_color:
            out.append('google_alternate_color = "%s";' %data.alternate_color)

        if data.color_border:
            out.append('google_color_border = "%s";' %data.color_border)

        if data.color_link:
            out.append('google_color_link = "%s";' %data.color_link)

        if data.color_url:
            out.append('google_color_url = "%s";' %data.color_url)

        if data.color_text:
            out.append('google_color_text = "%s";' %data.color_text)

        if data.alternate_ad_url:
            out.append('google_alternate_ad_url = "%s";' %data.alternate_ad_url)

        #out.append('google_ad_channel = "";')
        #out.append('google_ad_format = "";')
        #out.append('google_cpa_choice = "";')
        #out.append('google_ad_type = "text_image";')

        out.append('-->')

        return '\n'.join(out)


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IAdSensePortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IAdSensePortlet)
