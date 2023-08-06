"""

    Add header/image flash upload possibility.

    Extends Archetypes object to have additional Edit tab where header specific settings can be edited.

    Copy-pasted from https://svn.plone.org/svn/collective/collective.contentleadimage/trunk/collective/contentleadimage/extender.py

"""

__author__ = "Twinapex Research <research@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"

from Products.Archetypes.public import ImageField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from archetypes.schemaextender.field import ExtensionField
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender, ISchemaModifier
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import AnnotationStorage
from Products.Archetypes import public as atapi
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.Registry import registerWidget


from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher import NotFound
from Products.validation import V_REQUIRED

from Products.Archetypes.interfaces import IBaseObject

from plonetheme.twinapex.browser.interfaces import IThemeSpecific
from plonetheme.twinapex.interfaces import ILayoutImageable

from plonetheme.twinapex.browser.interfaces import IThemeSpecific

IMAGE_SIZE = (730,210)

IMAGE_FIELD_NAME = "headerImage"

ANIMATION_FIELD_NAME = "headerAnimation"

class LayoutimageImageField(ExtensionField, ImageField):
    """A Image field. """

    @property
    def sizes(self):
        sizes = {}
        sizes['leadimage'] = IMAGE_SIZE
        return sizes

class AnimationField(ExtensionField, atapi.FileField):
    """A Image field. """


class LayoutBooleanField(ExtensionField, atapi.BooleanField):
    pass

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class TitleWidget(atapi.StringWidget):
    """ Render title only when showTitle is set.


    """

    security  = ClassSecurityInfo()

    _properties = atapi.StringWidget._properties.copy()

    def __call__(self, mode, instance, context=None):
        """ Check instance whether it should show heading or not. """

        if mode == "view":
            field = instance.getField("showTitle")
            showTitleVal = field.get(instance)
            if showTitleVal == False:
                # Must not be None, as we might have extended a type
                # which do not have a default value
                return '' # when documentFirstHeading is empty, no extra line should be rendered

        return atapi.StringWidget.__call__(self, mode, instance, context)


registerWidget(TitleWidget,
               title='Title',
               description=('Hideable title support'),
               used_for=('Products.Archetypes.Field.StringField',)
               )


class LayoutSchemaModifier(object):
    """ Override Title renderer with a custom version.

    This is conditionally registered to Twinapex theme in configure.zcml.
    """
    implements(IBrowserLayerAwareExtender)
    adapts(ILayoutImageable)

    layer = IThemeSpecific

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        # Install a theme specific widget which is
        # able to hide heading if the header image is present


        # TODO: layer check by ATSE fails!!
        # manually check layer here
        request = getattr(self.context, "REQUEST", None)
        if request:
            if self.layer.providedBy(request):
                schema['title'].widget.macro = "title_widget"


class LayoutImageExtender(object):
    adapts(ILayoutImageable)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IThemeSpecific

    fields = [
        AnimationField("headerAnimation",
          schemata="layout",
          required = False,
          languageIndependent = False,
          validators = (('isNonEmptyFile', V_REQUIRED),),
          widget = atapi.FileWidget(
                         label="Header animimation",
                         description=u"You can upload header animation This Flash animation "
                                       u"will be displayed above the content.",
                         show_content_type=False,
                 ),
          ),

        LayoutimageImageField("headerImage",
          schemata="layout",
          required = False,
          storage = AnnotationStorage(migrate=True),
          languageIndependent = False,
          validators = (('isNonEmptyFile', V_REQUIRED),
                               ('checkNewsImageMaxSize', V_REQUIRED)),
          widget = ImageWidget(
                         label="Header image",
                         description=u"You can upload header image. This image "
                                       u"will be displayed above the content. "
                                       u"Uploaded image will be automatically "
                                       u"scaled to right size.",
                         show_content_type=False,
                 ),
        ),

        LayoutBooleanField("showTitle",
            schemata="layout",
            required= False,
            default = True,
            widget = atapi.BooleanWidget(label="Show title", description="Optionally hide document main title")
            ),

        LayoutBooleanField("fullWidth",
            schemata="layout",
            required= False,
            default = False,
            widget = atapi.BooleanWidget(label="Full width page", description="Front page style full width layout without breadcrumbs")
            )
        ]

    def __init__(self, context):
         self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        """
        'original' is a dictionary where the keys are the names of
        schemata and the values are lists of field names, in order.

        Move leadImage field just after the Description
        """
        return original



class LayoutImageTraverse(DefaultPublishTraverse):
    implements(IPublishTraverse)
    adapts(ILayoutImageable, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):

        if name.startswith(IMAGE_FIELD_NAME):
            field = self.context.getField(IMAGE_FIELD_NAME)
            if field is not None:
                return field.get(self.context)

        if name.startswith("showTitle"):
            field = self.context.getField("showTitle")
            if field is not None:
                return field.get(self.context)

        if name.startswith("fullWidth"):
            field = self.context.getField("fullWidth")
            if field is not None:
                return field.get(self.context)


        if name.startswith(ANIMATION_FIELD_NAME):
            field = self.context.getField(ANIMATION_FIELD_NAME)
            file = field.get(self.context)
            if file is not None and not isinstance(file, basestring):
                # image might be None or '' for empty images
                return file

        return super(LayoutImageTraverse, self).publishTraverse(request, name)


