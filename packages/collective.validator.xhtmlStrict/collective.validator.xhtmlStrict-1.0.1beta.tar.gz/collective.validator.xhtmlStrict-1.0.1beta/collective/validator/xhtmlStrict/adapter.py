from zope.interface import implements,alsoProvides
from zope.component import adapts

from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName 

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.newsitem import ATNewsItem
basic_atct = (ATDocument,ATEvent,ATNewsItem)

from urllib import quote,urlencode, urlopen
from xml.dom import minidom
from DateTime import DateTime
import string

from collective.validator.base.config import *
from collective.validator.base.interfaces.interfaces import *
from collective.validator.base.content import sendattachment
from collective.validator.base.content.ValidationTool import ValidationTool
from collective.validator.base.browser.adapter import Parser
from collective.validator.xhtmlStrict.interfaces import *

import tempfile

class W3cStrict(Parser):

    security = ClassSecurityInfo()

    implements(IW3cStrict)
    adapts(IVTPlone)

    val_url = "http://validator.w3.org/check"
    val_type = 'XHTML 1.0 Strict'

    def __init__(self, context):
        Parser.__init__(self,context)

    security.declarePrivate('getValidationResults')
    def getValidationResults(self, xhtml):
        """Returned structure:
        {'m:errors':{
                     'm:errorcount':2,
                     'm:errorlist':[
                                    {
                                     'm:line':1,
                                     'm:col':2,
                                     'm:message':'err message',
                                    },
                                    ...
                                   ],
                    },
        'm:warnings':{
                      'm:warningcount':1,
                      'm:warninglist':[
                                       {
                                        'm:line':1,
                                        'm:col':2,
                                        'm:message':'warn message',
                                       },
                                       ...
                                      ],
                      },
        'm:validity':true,
        }
        """     
        values = {'fragment': xhtml,
                  'verbose':'1',
                  'doctype':self.val_type, 
                  'output':'soap12'}
        
        params = urlencode(values)
        try:
            f = urlopen(self.val_url, params)
        except IOError:
            return 0
        return self.createResult(f.read())

    security.declareProtected(USE_VALIDATION_PERMISSION, 'runValidation')
    def runValidation(self):
        """Validate a site"""
        plone_utils = getToolByName(self.context,'plone_utils')
        results = self.search()
        fileout=""
        toterr = totwarn = nerr = nwarn = 0
        valid = True
        for document in results:
            document = document.getObject()
            validation = self.getValidationResults(document.view().encode('utf8'))
            if validation == 0:
                plone_utils.addPortalMessage("Connecting with the server problems")
                return 0
            partialReport, nerr, nwarn, valid_next = self.createReportPage(validation, document.Title(), document.absolute_url())
            fileout+= partialReport
            toterr+=nerr
            totwarn+=nwarn
            valid &=valid_next
        id_report = self.createReportDocument(fileout,toterr,totwarn,len(results),valid)
        
        #if email fields are set, send the report
        if self.context.getSendReport() and self.context.getEmailAddresses():
            self.sendReportAsAttach(self.createReportMail(fileout,toterr, totwarn,len(results)),("portal-validation-report",".html"))

        # try to do the 'hide' action; default plone workflow make visible contents accessible
        wtool = getToolByName(self.context,'portal_workflow')
        try:
            wtool.doActionFor(f, 'hide')
        except:
            pass
        
        str = "<a href='portal_validationtool/%s'>report</a> %s " %(id_report,self.val_type)
        str += self.translation_service.utranslate( \
                                           domain='collective.validator.xhtmlStrict', \
                                           msgid='strict_portal_message', \
                                           default="generated", \
                                           context=self.context)
        plone_utils.addPortalMessage(str)

       
    security.declareProtected(USE_VALIDATION_PERMISSION, 'runValidation')
    def runDebugValidation(self):
        """Validate other view of content types selected"""
        plone_utils = self.context.plone_utils
        portal = self.context.portal_url.getPortalObject()
        portal_types = self.context.getDebugTypesList()
        if not portal_types: return
        fileout = ""
        viewscount = 0
        toterr = totwarn = 0
        for type_name in portal_types:
            tmpid = portal.generateUniqueId(type_name)
            tmpobject = portal.restrictedTraverse('portal_factory/%s/%s' % (type_name, tmpid))
            tmpobject = self.setBaseType(tmpobject)        
            adapted = IValidable(tmpobject)
            ris, validation_report_list = adapted.isValid()
            viewscount+= len(validation_report_list)
            valid = True
            for report in validation_report_list:
                nerr = nwarn = 0
                partialReport, nerr, nwarn, valid_next = self.createReportPage(report[1], tmpobject.title_or_id(), tmpobject.absolute_url()+"/"+report[0])
                fileout+= partialReport
                toterr+=nerr
                totwarn+=nwarn
                valid &= valid_next
        id_report = self.createDebugReportDocument(fileout,toterr,totwarn,viewscount,valid)

        # try to do the 'hide' action; default plone workflow make visible contents accessible
        wtool = self.context.portal_workflow
        try:
            wtool.doActionFor(f, 'hide')
        except:
            pass
        
        if self.context.getSendReportDebug() and self.context.getEmailAddressesDebug():
            self.sendReportAsAttach(fileout,("portal-validation-report",".html"))
        
        str = "<a href='portal_validationtool/%s'>report</a> %s debug " %(id_report,self.val_type)
        str += self.translation_service.utranslate( \
                                           domain='collective.validator.xhtmlStrict', \
                                           msgid='strict_portal_message', \
                                           default="generated", \
                                           context=self.context)
        plone_utils.addPortalMessage(str)
        
    security.declarePrivate('setBaseType')
    def setBaseType(self, tmpobject):
        """if the object is in one of the basic content types set for it the IBaseValidableType
        interface. In other case do nothing...
        """
        for t in tmpobject.__class__.__bases__+(tmpobject.__class__,):
            if t in basic_atct:
                alsoProvides(tmpobject, IBaseValidationType)
                return tmpobject
        return tmpobject
