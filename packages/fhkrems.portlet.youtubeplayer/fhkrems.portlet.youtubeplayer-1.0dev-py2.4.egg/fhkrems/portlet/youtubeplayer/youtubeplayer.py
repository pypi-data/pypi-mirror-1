from zope.interface import implements
from zope.component import getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from fhkrems.portlet.youtubeplayer import YouTubePlayerMessageFactory as _

class IYouTubePlayer(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    url = schema.TextLine(
        title=_(u"VideoID"),
        description=_(u"ID of the youtube video"),
        required=True)

    width = schema.TextLine(
        title=_(u"Width"),
        description=_(u"Set width of Player"),
        required=True)

    height = schema.TextLine(
        title=_(u"Height"),
        description=_(u"Set height of Player incl. 25px of controls"),
        required=True)

    hl = schema.TextLine(
        title=_(u"Language"),
        description=_(u"For more Information look here: "
                      " http://code.google.com/apis/youtube/2.0/reference.html#Localized_Category_Lists"),
        required=True)

    rel = schema.Bool(
        title=_(u"Relational Videos"),
        description=_(u"Sets whether the player should load related videos "
                      " once playback of the initial video starts."),
        required=False,
        default=False)

    fs = schema.Bool(
        title=_(u"Fullscreen"),
        description=_(u"Setting to True enables the fullscreen button."),
        required=False,
        default=False)

    autoplay = schema.Bool(
        title=_(u"Autoplay"),
        description=_(u"Sets whether or not the initial video will autoplay when the player loads."),
        required=False,
        default=False)

    showinfo = schema.Bool(
        title=_(u"Show Information"),
        description=_(u"Setting to True causes the player to not display information like the video title and rating before the video starts playing."),
        required=False,
        default=False)

    footer = schema.TextLine(
        title=_(u"Portlet footer"),
        description=_(u"Text to be shown in the footer"),
        required=False)

    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_(u"Tick this box if you want to render the text above "
                      "without the standard header, border or footer."),
        required=True,
        default=False)

    hide = schema.Bool(
        title=_(u"Hide portlet"),
        description=_(u"Tick this box if you want to temporarily hide "
                      "the portlet without losing your text."),
        required=True,
        default=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IYouTubePlayer)
    header = _(u"title_static_portlet", default=u"Static text portlet")
    url = u""
    hl = u""
    height = u""
    width = u""
    rel = False
    fs = False
    autoplay = False
    showinfo = False
    omit_border = False
    footer = u""
    hide = False

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self, header=u"", url=u"", omit_border=False, footer=u"",
                 hl=u"", rel=False, fs=False, autoplay=False, showinfo=False, hide=False,):
        self.header = header
        self.url = url
        self.width = width
        self.height = height
        self.hl = hl
        self.rel = rel
        self.fs = fs
        self.autoplay = autoplay
        self.showinfo = showinfo
        self.omit_border = omit_border
        self.footer = footer
        self.hide = hide

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "YouTube Player"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('youtubeplayer.pt')

    @property
    def available(self):
        return not self.data.hide

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-static-%s" % normalizer.normalize(header)

    def has_footer(self):
        return bool(self.data.footer)

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IYouTubePlayer)
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
    form_fields = form.Fields(IYouTubePlayer)
    label = _(u"title_edit_static_portlet",
              default=u"Edit static text portlet")
    description = _(u"description_static_portlet",
                    default=u"A portlet which can display static HTML text.")
