import unittest
import zope.testing
	
from Products.PloneTestCase import PloneTestCase as ptc

from collective.validator.css.adapter import W3cCss
from collective.validator.css.interfaces.interfaces import ICss
from collective.validator.base.content.ValidationTool import ValidationTool


ptc.setupPloneSite(products=['collective.validator.base'])

class TestPloneValidation(ptc.PloneTestCase):

    def test_wrong_url(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        result = validator.getValidationResults('afgdfg')
        self.assertEquals(result, 0)

    def test_right_url(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        right = {'m:warnings': {'m:warninglist': [], 'm:warningcount': 0},'m:errors':{'m:errorlist': [], 'm:errorcount': 0},'m:validity': True}
        result = validator.getValidationResults('http://jigsaw.w3.org/css-validator/validator?uri=www.w3.org&output=soap12&profile=css21&usermedium=all')
        self.assertEquals(result, right)

    def test_empty_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        result = validator.dumpErrors("")
        self.assertEquals(result, "")
  
    def test_right_value_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        var = {'m:line':12,'m:message':'hello world','m:context':'my context','m:skippedstring': 'something'}
        value = []
        value.append(var)
        st = u"<dl><dt>%s/%s</dt><br><dd>row: %s</dd><dd>context: %s</dd><dd><em>%s %s</em></dd></dl>"

        stout= st % (1, 1, var['m:line'], var['m:context'], var['m:message'], var['m:skippedstring'])
        result = validator.dumpErrors(value)
        self.assertEquals(result, stout)

    def test_right_value_dumpWarnings(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        var = {'m:line':12,'m:message':'hello world'}
        value = []
        value.append(var)
        st = u"<dl><dt>%s/%s</dt><br><dd>row: %s</dd><dd><em>%s</em></dd></dl>"

        stout= st % (1, 1, var['m:line'], var['m:message'])
        result = validator.dumpWarnings(value)
        self.assertEquals(result, stout)


    def test_wrong_value_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        result = validator.dumpErrors('some string')
        self.assertEquals(result, "wrong list")




    def test_fakeCss(self):
        """try to create a string with a fake css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        str = validator.createQueryString('fake.css')
        self.assertEquals(str,'css not found')

    def test_validate_css_right(self):
        """try to validate a correct css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        str = validator.createQueryString('member.css')
        result = validator.getValidationResults(str)
        right = {'m:warnings': {'m:warninglist': [], 'm:warningcount': 0},'m:errors':{'m:errorlist': [], 'm:errorcount': 0},'m:validity': True}
        self.assertEquals(result,right)

    def test_validate_fakeCss(self):
        """try to validate a fake css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        str = validator.createQueryString('fake.css')
        result = validator.getValidationResults(str)
        self.assertEquals(result,0)


    def test_report_right(self):
        """create the report for a correct css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        str = validator.createQueryString('member.css')
        val = validator.getValidationResults(str)
        result, nerr, nwarn,validity = validator.createReportPage(val,'member.css')
        report = ""
        report+=u"""<h2>member.css</h2><br><p style="margin-top:0px;">"""
        report+="Validation success for member.css<br>"
        report+="</p>"
        self.assertEquals(result,report)
        self.assertEquals(nerr,0)
        self.assertEquals(nwarn,0)
        self.assertEquals(validity,True)

    def test_mail_body_css(self):
        """create the report for a correct css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = ICss(vt_context)
        str = validator.createQueryString('member.css')
        val = validator.getValidationResults(str)
        fileout, nerr, nwarn,validity = validator.createReportPage(val,'member.css')
        result = validator.createReportMail(fileout,nerr, nwarn,1)
        right = u'\
<html>\
<head>\
<title>Portal validation</title>\
</head>\
<body>\
<h3>Validation Results for Css</h3>\
<h3>0 errors, 0 warnings in 1 file(s)</h3>\
<h2>member.css</h2><br><p style="margin-top:0px;">Validation success for member.css<br></p><br></body></html>' 

        self.assertEquals(result,right)



ptc.setupPloneSite()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneValidation))
    return suite

