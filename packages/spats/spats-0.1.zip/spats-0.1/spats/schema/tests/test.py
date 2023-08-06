import sys
import os

sys.path.append('..')
config = 'schema.ini'

import schema
from validation import ValidationError

import unittest

class TestSchema(unittest.TestCase):

    def setUp(self):
        self.s = schema.Schema()
        self.s.read(config)
        
    def testGetSchema(self):
        self.s.getFields()

    def testGetById(self):
        res = self.s.getFields({'id':"vh_root"})
        assert len(res) == 1

    def testGetByWrongId(self):
        res = self.s.getFields({"id":"flooper"})
        assert not len(res)
        
    def testGetByWrongKey(self):
        self.assertRaises(AssertionError, self.s.getFields, {"flip":"flop"})

    def testGetValue(self):
        res = self.s.getField("vh_root")
        # default
        assert res.getValue() == "/"
    

    def testGetCategories(self):
        for cat in [
            "host",
            #"host,basic",
            "host,includes",
            "host,excludes",
            "general"]:
            self.s = schema.Schema()
            self.s.read(config, cat)
            if cat.find("host") < 0:
                pass
            else:
                print "Test for  category %s" % cat
                self.s.getField('site')
                print "pass"

    def testSetValue(self):
        res = self.s.getField("vh_root")
        # default
        res.setValue("blue")
        assert res.getValue() == "blue"

    def testSuccessfulValidation(self):
        res = self.s.getField('timeout')
        assert res.getProperty('validator') == 'integer'
        res.setValue('10')
        assert res.error is None

    def testFailedValidation(self):
        res = self.s.getField('timeout')
        assert res.getProperty('validator') == 'integer'
        res.setValue('a')
        assert isinstance(res.error, ValidationError)

    def testFieldWithoutValidator(self):
        res = self.s.getField('virtualdir')
        assert res.getProperty('validator') is None
        res.setValue('a')
        assert res.error is None



if __name__=='__main__':
    unittest.main()
