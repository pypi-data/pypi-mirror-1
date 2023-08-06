# -*- coding: utf-8 -*-

################################################################
# zopyx.ecardsng
#
# (C) 2006-2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tuebingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################

import uuid

from zope.interface import implements
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl import getSecurityManager
from DateTime import DateTime

from Products.CMFCore.permissions import ManagePortal, View, ModifyPortalContent, AccessContentsInformation, ListFolderContents
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATBTreeFolder, ATFolder
from Products.Archetypes.utils import make_uuid
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

try:
    from Products.Archetypes.public import *
except ImportError:
    from Products.LinguaPlone.public import *

from zopyx.ecardsng.config import PROJECTNAME

voc_columns = DisplayList(zip(range(1,8), range(1,8)))

email_template = """\
Hello %(recipient_name)s,

%(sender_name)s has sent you an ecard.

Click here to open the ecard:

   %(hostname)s/%(path)s/ecard_lookup?id=%(secret_id)s


Regards,
Your portal team
"""

subject_template = 'ECard von %(sender_name)s'
FOLDER_ID = 'ecards' 

class ECardsSavedFolder(ATBTreeFolder):
    """ Container for saved Ecards""" 
    archetype_name = portal_type = meta_type = "ECardsSavedFolder"
    allowed_content_types = ('ECard',)

registerType(ECardsSavedFolder, PROJECTNAME)


class ECardsFolder(ATFolder):
    """ Container for Ecards """

    content_icon = 'ecardsfolder_icon.gif'
    global_allow = 0

    schema = ATFolder.schema.copy() + \
          Schema((

               IntegerField('columns',
                            schemata='default',
                            default=4,
                            vocabulary=voc_columns,
                            widget=SelectionWidget(label='Images per column',
                                                   format='select',
                            )
                  ),

                StringField('subject_template',
                            default=subject_template,
                            accessor='getSubjectTemplate',
                            mutator='setSubjectTemplate',
                            schemata='default',
                            widget=StringWidget(label='Subject template',
                                                size=60,
                            )
                  ),

                StringField('body',
                            default=email_template,
                            accessor='getTemplate',
                            mutator='setTemplate',
                            schemata='default',
                            widget=TextAreaWidget(label='Email template',
                                                  rows=20,                      
                                                  cols=60,
                            )
                  ),

            ),) 


    filter_content_types = 1
    archetype_name = portal_type = meta_type = "ECardsFolder"
    allowed_content_types = ('ECardsSavedFolder', 'ECard')
    immediate_view = default_view = 'ecardsfolder_view'
    suppl_views = ()

    security = ClassSecurityInfo()

    security.declareProtected(View, 'getECardsFolder')
    def getECardsFolder(self):
        """ return ourselfs """
        return self

    security.declareProtected(View, 'getAvailableImages')
    def getAvailableImages(self):
        """ return available of images (published ones only
            for anonymous users)
        """

        username = getSecurityManager().getUser().getUserName()
        catalog = getToolByName(self, 'portal_catalog')
        result = catalog(portal_type='Image',
                         path='/'.join(self.getPhysicalPath()),
                         sort_on='getObjPositionInParent',
                        )
        return [b.getObject() for b in result]

    def manage_afterAdd(self, item,  container):
        super(ECardsFolder, self).manage_afterAdd(item, container)
        if not FOLDER_ID in self.objectIds():
            self.invokeFactory('ECardsSavedFolder', FOLDER_ID)
            folder  = self[FOLDER_ID]
            folder.manage_permission(View, ('Anonymous', 'Authenticated'), 0)
            folder.manage_permission(ListFolderContents, ('Manager', ), 0)
            folder.manage_permission(ModifyPortalContent, ('Manager',), 0)
            folder.setConstrainTypesMode(1)
            folder.setImmediatelyAddableTypes(('ECard',))
            folder.setLocallyAllowedTypes(('ECard',))

    def newECard(self, REQUEST):
        """ create a new ecard """

        id = str(uuid.uuid4())
        folder = self[FOLDER_ID]
        folder.invokeFactory('ECard', id)
        ecard = getattr(folder, id)

        # normal text fields
        for k, v in REQUEST.form.items():
            field = ecard.getField(k)
            if field:
                mutator = field.mutator
                getattr(ecard, mutator)(v)

        # send out email notification
        ecard.sendNotification()

        ecard.setEffectiveDate(DateTime())
        ecard.setExpirationDate(DateTime() + 30)

        # Allow anonymous users to create, edit and submit new ECards
        ecard.manage_permission(View, ('Anonymous', 'Authenticated'), 0)
        ecard.manage_permission(AccessContentsInformation, ('Anonymous', 'Authenticated'), 0)
        ecard.manage_permission(ModifyPortalContent, ('Manager',), 0)
        ecard.reindexObject()
        self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/ecard_lookup?id=%s' % ecard._secret_id)


    security.declareProtected(View, 'ecard_lookup')
    def ecard_lookup(self, id):
        """ Lookup an ecard by (secret id) """

        catalog = getToolByName(self, 'portal_catalog')
        for brain in catalog(portal_type='ECard', 
                             path='/'.join(self.getPhysicalPath())):
            ecard = brain.getObject()
            if ecard.secret_id() == id:
                return self.ecard_view(ecard=ecard, REQUEST=self.REQUEST)
        raise ValueError('No Ecard with id=%s found' % id)


    security.declareProtected(ManagePortal, 'deleteOlderThan')
    def deleteOlderThan(self, days=30.0):
        """ Remove all ecards older than XX days """

        catalog = getToolByName(self, 'portal_catalog')
        for brain in catalog(portal_type='ECard', 
                             path='/'.join(self.getPhysicalPath())):
            ecard = brain.getObject()
            if DateTime() - ecard.created() > days:
                ecard.aq_parent.manage_delObjects(ecards.getId())

        self.REQUEST.RESPONSE.redirect(self.absolute_url())

registerType(ECardsFolder, PROJECTNAME)


class ECard(ATCTContent):

    archetype_name = portal_type = meta_type = "ECard"
    content_icon = 'ecard_icon.gif'
    _at_rename_after_creation = True
    _secret_id = None
    global_allow = 0

    default_view = immediate_view = 'ecard_view'

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/ecard_view',
                'permissions': (View,)
                },)

    schema = ATCTContent.schema.copy() + \
          Schema((

              StringField('title',
                          mutator='setTitle',
                          accessor='Title',
                          mode=''),

              StringField('image_id',
                          accessor='getImageId',
                          required=1,
                          ),

              StringField('sender_name',
                          required=1,
                          widget=StringWidget(label='Sender name',
                          )),

              StringField('sender_email',
                          required=1,
                          validators=('isEmail',),
                          widget=StringWidget(label='Sender email',
                          )
                  ),

              StringField('recipient_name',
                          required=1,
                          widget=StringWidget(label='Recipient name',
                          )
                  ),
              StringField('recipient_email',
                          required=1,
                          validators=('isEmail',),
                          widget=StringWidget(label='Recipient email',
                          )
                  ),

              StringField('email_body',
                          required=1,
                          widget=TextAreaWidget(label='Body',
                                                rows=15,
                                                cols=60,
                          )
                  ),

              BooleanField('emailSent',
                           default=0,
                           mode='rw',
                           accessor='getEmailSent',
                           mutator='setEmailSent',
                           widget=BooleanWidget(label='EMail sent',
                                                visible=0),
                 ),

            ))

    security = ClassSecurityInfo()

    def manage_afterAdd(self, item, container):
        if not self._secret_id:
            self._secret_id = str(uuid.uuid4())
        return ATCTContent.manage_afterAdd(self, item, container) 


    def sendNotification(self, resend=0):
        # don't publish

        site_encoding = self.portal_properties.site_properties.default_charset

        if self.getEmailSent() and not resend:
            raise ValueError('Email already sent')

        d = {'sender_name' : self.getSender_name(),
            'sender_email' : self.getSender_email(),
            'recipient_name' : self.getRecipient_name(),
            'recipient_email' : self.getRecipient_email(),
            'path' : self.getECardsFolder().absolute_url(1),
            'secret_id' : self.secret_id(),
            'hostname' : self.REQUEST.BASE0,
        }

        subject = self.getECardsFolder().getSubjectTemplate() % d
        subject = unicode(subject, site_encoding).encode('iso-8859-15')

        template = self.getTemplate()
        mail = template % d
        mail = unicode(mail, site_encoding).encode('iso-8859-15')

        self.MailHost.send(mail, (d['recipient_email'],) , d['sender_email'], subject)
        self.setEmailSent(True)


    security.declareProtected(ManagePortal, 'secret_id')
    def secret_id(self):
        """ return the secret id """
        return self._secret_id

    def processForm(self, data=1, metadata=0, REQUEST=None, values=None):
        """ Revoke ModifyPortalContent from Anonymous upon save operation"""
        ATCTContent.processForm(self, data, metadata, REQUEST, values)
        self.manage_permission(ModifyPortalContent, ('Manager',), 0)
registerType(ECard, PROJECTNAME)

