from zope.interface import implements,alsoProvides
from zope.component import adapts

from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName 
#from Products.PortalTransforms.transforms.safe_html import register

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.newsitem import ATNewsItem
basic_atct = (ATDocument,ATEvent,ATNewsItem)

from urllib import quote,urlencode, urlopen
from xml.dom import minidom
from DateTime import DateTime

import string
import tempfile

from collective.validator.base.config import *
from collective.validator.base.interfaces.interfaces import *
from collective.validator.base.content import sendattachment
from collective.validator.base.content.ValidationTool import ValidationTool
from collective.validator.base.browser.adapter import Parser
from collective.validator.css.interfaces import *

class W3cCss(Parser):

    security = ClassSecurityInfo()

    implements(ICss)
    adapts(IVTPlone)

    val_url = "http://jigsaw.w3.org/css-validator/validator"
    val_type = "Css"

    def __init__(self, context):
        Parser.__init__(self, context)
   
    security.declarePrivate('getValidationResults')
    def getValidationResults(self, str):
        """Returned structure:
        {'m:errors':{
                     'm:errorcount':2,
                     'm:errorlist':[
                                    {
                                     'm:line':1,
                                     'm:context':'',
                                     'm:message':'Parse error',
                                     'm:skippedstring':'repeat;',
                                    },
                                    ...
                                   ],
                    },
        'm:warnings':{
                      'm:warningcount':1,
                      'm:warninglist':[
                                       {
                                        'm:line':1,
                                        'm:message':'warn message',
                                       },
                                       ...
                                      ],
                      },
        'm:validity':true,
        }
        """
        try:
            f = urlopen(str)
        except IOError:
            return 0
        xmldoc = minidom.parseString(f.read())
        return self.createResult(xmldoc)
       
    security.declarePrivate('createResult')
    def createResult(self,xmldoc):
        """create the structure for the report..it's a little different from the xhtml-report-structure"""
        results = {'m:errors':{'m:errorcount':0,
                               'm:errorlist':[],
                              },
                   'm:warnings':{'m:warningcount':0,
                                 'm:warninglist':[],
                                },
                   'm:validity':None,
                  }

        errors = xmldoc.getElementsByTagName('m:error')
        err_results = []
        for err in errors:
            diz = {}
            diz['m:line'] = int(err.getElementsByTagName('m:line')[0].childNodes[0].nodeValue)
            diz['m:message'] = err.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
            diz['m:context'] = err.getElementsByTagName('m:context')[0].childNodes[0].nodeValue
            diz['m:skippedstring'] = err.getElementsByTagName('m:skippedstring')[0].childNodes[0].nodeValue
            err_results.append(diz)
        errs = results['m:errors']
        errs['m:errorcount'] = len(err_results)
        errs['m:errorlist'] = err_results
        results['m:errors'] = errs

        warnings = xmldoc.getElementsByTagName('m:warning')
        warn_results = []
        for warn in warnings:
            diz = {}
            diz['m:line'] = int(warn.getElementsByTagName('m:line')[0].childNodes[0].nodeValue)
            diz['m:message'] = warn.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
            warn_results.append(diz)   
        warns = results['m:warnings']
        warns['m:warningcount'] = len(warn_results)
        warns['m:warninglist'] = warn_results
        results['m:warnings'] = warns
        results['m:validity'] = xmldoc.getElementsByTagName('m:validity')[0].childNodes[0].nodeValue == 'true'
        return results

    security.declarePrivate('dumpErrors')
    def dumpErrors(self, elist):
        """Render html for validation error structure"""
        stout = "<dl>"
        st = "<dt>%s/%s</dt><br><dd>"
        st += self.translation_service.utranslate( \
                                           domain='collective.validator.css', \
                                           msgid='row', \
                                           default="row:", \
                                           context=self.context)
        st +=" %s</dd><dd>"
        st += self.translation_service.utranslate( \
                                           domain='collective.validator.css', \
                                           msgid='context', \
                                           default="context:", \
                                           context=self.context)
        st +=" %s</dd><dd><em>%s %s</em></dd>"
        cnt = 0
        elen = len(elist)
        if not elen: return ""
        try:
            for x in elist:
                cnt+=1
                stout+= st % (cnt, elen, x['m:line'], x['m:context'], x['m:message'], x['m:skippedstring'])
            return stout+"</dl>"
        except:
            return "wrong list"

    security.declarePrivate('dumpWarnings')
    def dumpWarnings(self, elist):
        """Render html for validation warning structure"""
        stout = "<dl>"
        st = "<dt>%s/%s</dt><br><dd>"
        st += self.translation_service.utranslate( \
                                           domain='collective.validator.css', \
                                           msgid='row', \
                                           default="row:", \
                                           context=self.context)
        st +=" %s</dd><dd><em>%s</em></dd>"
        cnt = 0
        elen = len(elist)
        if not elen: return ""
        try:
            for x in elist:
                cnt+=1
                stout+= st % (cnt, elen, x['m:line'], x['m:message'])
            return stout+"</dl>"
        except:
            return "wrong list"

    security.declarePublic('createReport')
    def createReportPage(self, validation,css):
        """Create the HTML output report for a given HTML source"""
        report = ""
        report+="""<h2>%s</h2><br><p style="margin-top:0px;">""" % (css)
        parerr = parwarn = 0
        if validation['m:validity']:
            report+= self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='success_valid', \
                                           default="Validation success for", \
                                           context=self.context)
            report+= " %s<br>" %css
        else:
            report+= self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='unsuccess_valid', \
                                           default="Validation failed for", \
                                           context=self.context)
            report+= " %s<br>" %css

            if validation.get('m:errors',None):
                parerr = parerr + validation['m:errors']['m:errorcount']
                report += self.createReportErr(validation['m:errors']['m:errorcount'])
                report+=str(self.dumpErrors(validation['m:errors']['m:errorlist']))
            if validation.get('m:warnings',None):
                parwarn = parwarn + validation['m:warnings']['m:warningcount']
                report += self.createReportWarn(validation['m:warnings']['m:warningcount'])
                report+=str(self.dumpWarnings(validation['m:warnings']['m:warninglist']))
        report+="</p>"
        return (report, parerr, parwarn,validation['m:validity'])

    security.declareProtected(USE_VALIDATION_PERMISSION, 'runValidation')
    def runValidation(self):
        """Validate css in portal_css"""
        plone_utils = getToolByName(self.context,'plone_utils')
        portal = getToolByName(self.context,'portal_css')
        css_list = portal.getResourceIds() 
        fileout = ""
        toterr = totwarn = nerr = nwarn = 0
        valid = True
        for css in css_list:         
            validation = self.getValidationResults(self.createQueryString(css))
            partialReport, nerr, nwarn,valid_next = self.createReportPage(validation, css)
            fileout+= partialReport
            toterr+=nerr
            totwarn+=nwarn
            valid &=valid_next
        id_report = self.createReportDocument(fileout,toterr,totwarn,len(css_list),valid)
    
        #if email fields are set, send the report
        if self.context.getSendReport() and self.context.getEmailAddresses():
            self.sendReportAsAttach(self.createReportMail(fileout,toterr, totwarn,len(css_list)),("portal-validation-report",".html"))

        # try to do the 'hide' action; default plone workflow make visible contents accessible
        wtool = getToolByName(self.context,'portal_workflow')
        try:
            wtool.doActionFor(f, 'hide')
        except:
            pass
        str = "<a href='portal_validationtool/%s'>report</a> %s " %(id_report,self.val_type)
        str += self.translation_service.utranslate( \
                                           domain='collective.validator.css', \
                                           msgid='css_portal_message', \
                                           default="CSS generated", \
                                           context=self.context)
        plone_utils.addPortalMessage(str)

    security.declarePrivate('createQueryString')
    def createQueryString(self,css):
        """create a string for the validation request"""
        try:
            appo = self.context.portal_css[css]
        except:
            return 'css not found'
        s = ''.join(appo)
        code = string.replace(s,"\n"," ")
        code_app = code.rstrip(' text/css;charset=utf-8')
        code = quote(code_app)
        str = quote("\"")
        params = "text=%s&output=soap12" %(code)
        validator = W3cCss.val_url + "?"
        return validator + params
