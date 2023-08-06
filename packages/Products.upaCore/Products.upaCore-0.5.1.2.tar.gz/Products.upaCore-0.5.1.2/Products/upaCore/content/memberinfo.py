# -*- coding: iso-8859-15 -*-

################################################################
# upaCore
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################


import os
import tempfile
import transaction

from zope.interface import implements
from AccessControl.SecurityInfo import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.ATContentTypes.configuration import zconf
from Products.CMFCore.permissions import ModifyPortalContent, View, ManageUsers
from Products.CMFCore.utils import getToolByName
from Products.validation import V_REQUIRED
from DateTime.DateTime import DateTime
from Products.CMFPlone.utils import scale_image
from OFS.Image import Image

from Products.upaCore.config import PROJECTNAME
from Products.upaCore.permissions import upacoreViewInternally


salutation_vocabulary = DisplayList((('Mr.', 'Mr.'), 
                                    ('Mrs.', 'Mrs.')))

membership_vocabulary = DisplayList((('Professional', 'Professional'), 
                                    ('Young Professional', 'Young Professional')))

country_vocabulary = DisplayList((('Germany', 'Germany'), 
                                  ('Swiss', 'Swiss'),
                                  ('Austria', 'Austria'),
                                  ('France', 'France'),
                                  ('Liechtenstein', 'Lichtenstein'),
                                  ('Italy', 'Italy'),
                                  ('Poland', 'Poland'),
                                ))


MemberInfoSchema = ATContentTypeSchema.copy() + Schema((
    StringField('salutation',
              required=True,
              vocabulary=salutation_vocabulary,
              widget = SelectionWidget(
                        description = '',
                        label=u'Salutation',
                        label_msgid='label_salutation_text',
                        i18n_domain='plone',
                        format='select',
    )),
    StringField('academicTitle',
              widget = StringWidget(
                        description = '',
                        label=u'Akademic title',
                        label_msgid='label_academic_title_text',
                        i18n_domain='plone',
                        size=60,
    )),
    StringField('firstName',
              required=True,
              searchable=True,
              widget = StringWidget(
                        description = '',
                        label=u'First name',
                        label_msgid='label_firstname_text',
                        i18n_domain='plone',
                        size=60,
    )),
    StringField('lastName',
              required=True,
              searchable=True,
              widget = StringWidget(
                        description = '',
                        label=u'Last name',
                        label_msgid='label_lastname_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('address1',
              required=True,
              searchable=True,
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Address 1',
                        label_msgid='label_address1_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('address2',
              required=False,
              searchable=True,
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Address 2',
                        label_msgid='label_address2_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('zipCode',
              required=True,
              searchable=True,
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'ZIP code',
                        label_msgid='label_zipcode_text',
                        i18n_domain='plone',
                        size = 8,
    )),
    StringField('city',
              required=True,
              searchable=True,
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'City',
                        label_msgid='label_city_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('country',
              required=True,
              default='germany',
              vocabulary=country_vocabulary,
              read_permission=upacoreViewInternally,
              widget = SelectionWidget(
                        description = '',
                        label=u'Country',
                        label_msgid='label_country_text',
                        i18n_domain='plone',
                        format='select',
    )),
    StringField('phone',
              required=False,
              searchable=True,
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Phone',
                        label_msgid='label_phone_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('mobile',
              required=False,
              searchable=True,
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Mobile',
                        label_msgid='label_mobile_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('fax',
              required=False,
              searchable=True,
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Fax',
                        label_msgid='label_fax_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('emailPrivate',
              searchable=True,
              required=False,
              validators = ('isEmail',),
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Email (private)',
                        label_msgid='label_email_private_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('emailCompany',
              searchable=True,
              required=True,
              validators = ('isEmail',),
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Email (Company)',
                        label_msgid='label_email_company_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('organization',
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Organization',
                        label_msgid='label_organization_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    StringField('associatedMembership',
              read_permission=upacoreViewInternally,
              widget = StringWidget(
                        description = '',
                        label=u'Associated membership',
                        label_msgid='label_associated_membership_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    TextField('text',
               searchable=True,
               storage = AnnotationStorage(migrate=True),
               accessor='getText',
               mutator='setText',
               validators = ('isTidyHtmlWithCleanup',),
               #validators = ('isTidyHtml',),
               default_content_type = zconf.ATDocument.default_content_type,
               default_output_type = 'text/x-html-safe',
               allowable_content_types = zconf.ATDocument.allowed_content_types,
               widget = RichWidget(
                        label=u'My professional information',
                        label_msgid='label_my_info_text',
                        i18n_domain='plone',
                        rows = 10,
    )),
    ImageField('image',
                required=False,
                storage = AnnotationStorage(migrate=True),
                languageIndependent = True,
                sizes= {'large'   : (768, 768),
                        'preview' : (400, 400),
                        'mini'    : (200, 200),
                        'thumb'   : (128, 128),
                        'tile'    :  (64, 64),
                        'icon'    :  (32, 32),
                        'listing' :  (16, 16),
                       },
                validators = (('isNonEmptyFile', V_REQUIRED),),
                widget = ImageWidget(
                                label=u'Portrait',
                                label_msgid='label_portrait_text',
                                i18n_domain='plone',
    )),
    BooleanField('newsletterSubscription',
              default=False,
              read_permission=upacoreViewInternally,
              widget = BooleanWidget(
                        description = '',
                        label=u'Newsletter subscription',
                        label_msgid='label_newsletter_subscription_text',
                        i18n_domain='plone',
    )),
    BooleanField('icomSubscription',
              default=False,
              read_permission=upacoreViewInternally,
              widget = BooleanWidget(
                        description = '',
                        label=u'ICOM subscription',
                        label_msgid='label_icom_subscription_text',
                        i18n_domain='plone',
    )),

    StringField('membershipLevel',
              default='full',
              vocabulary=membership_vocabulary,
              read_permission=View,
              write_permission=ManageUsers,
              schemata='Membership',
              widget = SelectionWidget(
                        description = '',
                        label=u'Membership level',
                        label_msgid='label_membership_level_text',
                        i18n_domain='plone',
                        format='select',
    )),
    StringField('entryDate',
              default='',
              read_permission=ManageUsers,
              write_permission=ManageUsers,
              schemata='Membership',
              widget = StringWidget(
                        description = '',
                        label=u'Entry date',
                        label_msgid='label_entry_date_text',
                        i18n_domain='plone',
                        size = 60,
    )),
    IntegerField('upaId',
              required=True,
              default=0,
              read_permission=ManageUsers,
              write_permission=ManageUsers,
              validators = ('isInt',),
              schemata='Membership',
              widget = StringWidget(
                        description = '',
                        label=u'UPA Member ID',
                        label_msgid='label_upa_member_id_text',
                        i18n_domain='plone',
                        size = 8,
    )),
    BooleanField('accountActive',
              default=True,
              read_permission=View,
              write_permission=ManageUsers,
              schemata='Membership',
              widget = BooleanWidget(
                        description = '',
                        label=u'Account active',
                        label_msgid='label_account_active_text',
                        i18n_domain='plone',
                        format='select',
    )),
    ),
    marshall=RFC822Marshaller(),
    )

MemberInfoSchema['id'].default = 'index_html'
MemberInfoSchema['id'].mutator = 'setForcedId'
MemberInfoSchema['title'].mode = 'r'

for id in ('allowDiscussion', 'excludeFromNav', 'description', 
           'contributors', 'creators', 'rights', 'subject', 'location', 
           'language', 'relatedItems', 'effectiveDate', 'expirationDate',
          ):
    MemberInfoSchema[id].widget.visible = {'edit' : 'hidden', 'view' : 'hidden'}
    MemberInfoSchema[id].mode = 'r'

finalizeATCTSchema(MemberInfoSchema)


class MemberInfo(ATCTContent, HistoryAwareMixin):
    """ upaMemberInfo"""

    __implements__ = (ATCTContent.__implements__,
                      HistoryAwareMixin.__implements__,
                     )

    archetype_name = portal_type = meta_type = "MemberInfo"
    security = ClassSecurityInfo()
    schema = MemberInfoSchema

    admin_notified = False

    security.declareProtected(ModifyPortalContent, 'setForcedId')
    def setForcedId(self, value, **kwargs):
        if self.getId() != 'index_html':
            transaction.savepoint(1)
            self.setId('index_html')


    security.declareProtected(View, 'Title')
    def Title(self):
        """ return a custom title """
        return 'MemberInfo: %s, %s' % (self.getLastName(), self.getFirstName())

    def at_post_edit_script(self):
        """ Set some values automatically """

        pm = getToolByName(self, 'portal_membership')
        try:
            # Manager
            creator = self.getOwner().getUserName()
            member = pm.getMemberById(creator)
        except:
            # Standard member
            member = pm.getAuthenticatedMember()

        # ensure that the entry date is set
        entry_date = self.getEntryDate()
        if not entry_date:
            self.setEntryDate(DateTime().strftime('%d.%m.%Y'))

        # sync email to member properties
        email = self.getEmailCompany()
        if email:
            member.setMemberProperties(dict(email=email))

        # sync image to portrait

        img = self.getImage()
        image_data = None
        if isinstance(img, str):
            image_data = img
        else:
            try:
                image_data = str(img.data)
            except:
                pass

        if image_data:
            fname = tempfile.mktemp()
            file(fname, 'wb').write(image_data)
            scaled, mimetype = scale_image(fname)
            portrait = Image(id=member.getUserName(), file=scaled, title='')
            membertool = getToolByName(self, 'portal_memberdata')
            membertool._setPortrait(portrait, member.getUserName())
            os.unlink(fname)

        if not hasattr(self, .admin_notified):
            msg = 'Neue Registrierung: %s' % self.absolute_url()
            try:
                toAddr = context.portal_properties.upa.registration_notification
            except:
                toAddr = 'mm@ergonomicon.de',

            self.MailHost.secureSend(msg,
                                     toAddr,
                                     'mm@ergonomicon.de',
                                     '[GermanUPA] neue Registrierung: %s' % member.getUserName())
            self.admin_notified = True



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

        return super(ATCTContent, self).__bobo_traverse__(REQUEST, name)

registerType(MemberInfo, PROJECTNAME)

