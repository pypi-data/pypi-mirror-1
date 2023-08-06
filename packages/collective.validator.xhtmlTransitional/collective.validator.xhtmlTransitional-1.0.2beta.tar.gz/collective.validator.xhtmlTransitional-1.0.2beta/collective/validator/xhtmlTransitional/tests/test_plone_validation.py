import unittest
import zope.testing
	
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName 
#from Products.PortalTransforms.transforms.safe_html import register

from Products.PloneTestCase import PloneTestCase as ptc

from collective.validator.xhtmlTransitional.adapter import W3cTransitional
from collective.validator.xhtmlTransitional.interfaces.interfaces import IW3cTransitional
from collective.validator.base.content.ValidationTool import ValidationTool

class TestPloneStrict(ptc.PloneTestCase):

    def test_trans_wrong_text_result(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        result = validator.getValidationResults('afgdfg')
        right = {'m:warnings': {'m:warninglist': [{'m:col': 0,
                                                   'm:line': 0,
                                                   'm:message': u'Unable to Determine Parse Mode!'},
                                                  {'m:col': 0,
                                                   'm:line': 0,
                                                   'm:message': u'DOCTYPE Override in effect!'}],
                                'm:warningcount': 2},
                 'm:errors': {'m:errorlist': [{'m:col': 0,
                                               'm:line': 1,
                                               'm:message': u'character "a" not allowed in prolog'},
                                              {'m:col': 6,
                                               'm:line': 1,
                                               'm:message': u'end of document in prolog'}],
                              'm:errorcount': 2},
                 'm:validity': False}
        self.assertEquals(result, right)

    def test_trans_create_result_right(self):
        """try to validate a correct css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        self.folder.invokeFactory('Document', id='doc')
        validation = validator.getValidationResults(self.folder.doc().encode('utf8'))
        right = {'m:warnings': {'m:warninglist': [], 'm:warningcount': 0}, 
                 'm:errors': {'m:errorlist': [], 'm:errorcount': 0}, 
                 'm:validity': True}
        self.assertEquals(validation,right)

    def test_trans_search(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        self.folder.invokeFactory('Document', id='doc')
        result = validator.search()
        self.assertEquals(len(result), 1)

    def test_trans_empty_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        result = validator.dumpErrors("")
        self.assertEquals(result, "")
  
    def test_trans_right_value_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        var = {'m:line':12,'m:message':'hello world','m:col':5}
        value = []
        value.append(var)
        st = "\
<dl><dt>%s/%s</dt><br>\
<dd>row: %s, column: %s</dd><dd><em>%s</em></dd></dl>" % (1, 1, var['m:line'], var['m:col'], var['m:message'])
        result = validator.dumpErrors(value)
        self.assertEquals(result, st)

    def test_trans_wrong_value_dumpErrors(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        result = validator.dumpErrors('some string')
        self.assertEquals(result, "wrong list")

    def test_trans_report_strict(self):
        """create the report"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        self.folder.invokeFactory('Document', id='doc')
        validation = validator.getValidationResults(self.folder.doc().encode('utf8'))
        result, nerr, nwarn,validity = validator.createReportPage(validation,self.folder.doc.Title(), 'www.plone.org')
        report = '\
<h2></h2><pre><a href="www.plone.org">www.plone.org</a></pre><p style="margin-top:0px;">Page validation succesfull<br></p><br>'

        self.assertEquals(result,report)
        self.assertEquals(nerr,0)
        self.assertEquals(nwarn,0)
        self.assertEquals(validity,True)

    def test_trans_right_description(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        result = validator.createDescription(5,1,2)
        self.assertEquals(result, '5 errors, 1 warnings in 2 file(s)')

    def test_trans_right_ReportErr(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        result = validator.createReportErr(2)
        self.assertEquals(result, '<h3>Found 2 errors</h3>')

    def test_trans_right_ReportWarn(self):
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        result = validator.createReportWarn(5)
        self.assertEquals(result, '<h3>Found 5 warnings</h3>')





    def test_trans_mail_body(self):
        """create the report for a correct css"""
        vt_id = 'validation_tool'
        vt = ValidationTool(vt_id)
        vt_id = self.portal._setObject(vt_id, vt)
        vt_context = self.portal[vt_id]
        validator = IW3cTransitional(vt_context)
        self.folder.invokeFactory('Document', id='doc',title='Some Title')
        validation = validator.getValidationResults(self.folder.doc().encode('utf8'))
        fileout,nerr,nwarn, validity = validator.createReportPage(validation,self.folder.doc.Title(), 'www.plone.org')
        result = validator.createReportMail(fileout,nerr, nwarn,1)
        right = '\
<html><head><title>Portal validation</title></head>\
<body><h3>Validation Results for XHTML 1.0 Transitional</h3>\
<h3>0 errors, 0 warnings in 1 file(s)</h3><h2>Some Title</h2>\
<pre><a href="www.plone.org">www.plone.org</a></pre><p style="margin-top:0px;">Page validation succesfull<br></p><br><br></body></html>'

        self.assertEquals(result,right)

    
ptc.setupPloneSite()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPloneStrict))
    return suite

