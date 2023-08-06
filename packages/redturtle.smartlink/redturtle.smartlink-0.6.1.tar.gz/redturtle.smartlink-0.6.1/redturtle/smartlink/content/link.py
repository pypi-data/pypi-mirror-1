"""Definition of the SmartLink content type
"""

import urlparse
from urllib import quote

from zope import interface
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import AnnotationStorage

from Products.CMFCore import permissions

from Products.ATContentTypes.content.link import ATLink, ATLinkSchema
from Products.ATReferenceBrowserWidget import ATReferenceBrowserWidget

from redturtle.smartlink import smartlinkMessageFactory as _
from redturtle.smartlink.interfaces import ISmartLink, ISmartLinked
from redturtle.smartlink.config import PROJECTNAME

from Products.ATContentTypes.configuration import zconf
from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED
from zope.component import queryUtility
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig
from Products.CMFPlone.utils import getToolByName

LinkSchema = ATLinkSchema.copy() + atapi.Schema((

    # HIDDEN!
    atapi.StringField('remoteUrl',
        searchable=True,
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_url', default=u'URL'),
            visible={'view': 'invisible', 'edit': 'invisible' },
        )
    ),

    atapi.StringField("externalLink",
              searchable=True,
              required=False,
              widget=atapi.StringWidget(
                    label= _(u'label_smartlink_externallink', default='External Link'),
                    description = _(u'help_smartlink_externallink',
                                    default=u"Enter the web address for a page which is not located on this server."),
                    i18n_domain='redturtle.smartlink',
                    size=50,
              )
    ),

    atapi.ReferenceField("internalLink",
                   default=None,
                   relationship="internal_page",
                   multiValued=False, 
                   widget=ATReferenceBrowserWidget.ReferenceBrowserWidget(
                        label= _(u'label_smartlink_internallink', default='Internal link'),
                        description = _(u'help_smartlink_internallink',
                                        default=u"Browse to find the internal page to which you wish to link. If this field is used, then any entry in the external link field will be ignored. You cannot have both an internal and external link."),
                        force_close_on_insert = True,
                        i18n_domain='redturtle.smartlink',
                    )
    ),

    atapi.ImageField('image',
        required = False,
        storage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        max_size = zconf.ATNewsItem.max_image_dimension,
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkNewsImageMaxSize', V_REQUIRED)),
        widget = atapi.ImageWidget(
            description = _(u'help_smartlink_image', default=u"Will be shown views that render content's images and in the link view itself"),
            label= _(u'label_smartlink_image', default=u'Image'),
            i18n_domain='redturtle.smartlink',
            show_content_type = False)
        ),

    atapi.StringField('imageCaption',
        required = False,
        searchable = True,
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_image_caption', default=u'Image Caption'),
            i18n_domain='redturtle.smartlink',
            size = 40)
        ),

))

LinkSchema['title'].storage = atapi.AnnotationStorage()
LinkSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(LinkSchema, moveDiscussion=False)

class SmartLink(ATLink):
    """A link to an internal or external resource."""
    interface.implements(ISmartLink)

    meta_type = "ATLink"
    schema = LinkSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    internalLink = atapi.ATReferenceFieldProperty('internalLink')
    
    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        return self.getField('image').tag(self, **kwargs)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATLink.__bobo_traverse__(self, REQUEST, name)

    security.declareProtected(permissions.ModifyPortalContent, 'setExternalLink')
    def setExternalLink(self, value, **kwargs):
        """remote url mutator
        Use urlparse to sanify the url
        Also see http://dev.plone.org/plone/ticket/3296
        """
        if value:
            value = urlparse.urlunparse(urlparse.urlparse(value))
        self.getField('externalLink').set(self, value, **kwargs)
        self.setRemoteUrl(self.getRemoteUrl())

    security.declareProtected(permissions.ModifyPortalContent, 'setInternalLink')
    def setInternalLink(self, value, **kwargs):
        self.getField('internalLink').set(self, value, **kwargs)
        self.setRemoteUrl(self.getRemoteUrl())

    def getRemoteUrl(self):
        """Return the URL of the link from the appropriate field, internal or external."""
        
        # We need to check if the self object has the reference_catalog attribute. It's an integration problem
        # with p4a that call this method when we don't have an internal link.
        if hasattr(self, 'reference_catalog'):
            ilink = self.getInternalLink()
        else:
            ilink = None
        if ilink:
            if queryUtility(ISmartlinkConfig,name="smartlink_config").relativelink:            
                object = self.getField('internalLink').get(self)
                remote = '/'.join(object.getPhysicalPath())
                return quote(remote, safe='?$#@/:=+;$,&%')
            else:
                remote = ilink.absolute_url()
        else:
            remote = self.getExternalLink()

        if not remote: remote = '' # ensure we have a string
        backendlinks = queryUtility(ISmartlinkConfig,name="smartlink_config").backendlink
        for backendlink in backendlinks:
            if backendlink[backendlink.__len__()-1:]=='/':
                blink = backendlink[:-1]
            else:
                blink = backendlink
            if remote.startswith(blink):
                frontendlinks = queryUtility(ISmartlinkConfig,name="smartlink_config").frontendlink
                frontendlink = frontendlinks[backendlinks.index(backendlink)]
                if frontendlink[frontendlink.__len__()-1:]=='/':
                    frontendlink = frontendlink[:-1]
                remote = remote.replace(blink,frontendlink)
        return quote(remote, safe='?$#@/:=+;$,&%')

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, remote_url=None, **kwargs):
        if not remote_url:
            remote_url = kwargs.get('remote_url', None)
        self.update(externalLink = remote_url, **kwargs)

    def post_validate(self, REQUEST, errors):
        """Check to make sure that either an internal or external link was supplied."""

        if not REQUEST.form.get('externalLink') and not REQUEST.form.get('internalLink'):
            xlink=REQUEST.get('externalLink', None)
            ilink=REQUEST.get('internalLink', None)
            if (not xlink and not ilink):
                errors['externalLink'] = _("label_internallink_externallink",default=u'You must either select an internal link or enter an external link. You cannot have both.')
            return errors
        if REQUEST.form.get('externalLink') and REQUEST.form.get('internalLink'):
            errors['externalLink'] = _("label_internallink_externallink",default=u'You must either select an internal link or enter an external link. You cannot have both.')
            return errors

    security.declarePrivate('_processForm')
    def _processForm(self, data=1, metadata=None, REQUEST=None, values=None):
        """BBB: I need to check old value before change it...
        I don't find a good place where to put this code. Zope3 Event don't help me"""
        form = self.REQUEST.form
        target = self.getInternalLink()
        if target and target.UID()!=form.get('internalLink') and ISmartLinked.providedBy(target):
            interface.noLongerProvides(target, ISmartLinked)
        ATLink._processForm(self, data=data, metadata=metadata, REQUEST=REQUEST, values=values)

atapi.registerType(SmartLink, PROJECTNAME)