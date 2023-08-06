from Products.Archetypes.atapi import *
from Products.Archetypes.tests.test_fields import FakeRequest
from Products.Archetypes.tests.test_fields import DummyVocabulary

from medialog.fullnamefield.field import FullnameField 
from medialog.fullnamefield.tests.base import FullnameFieldTestCase 


field_instances = [FullnameField('fullnamefield')]

field_values = {'fullname':'John Doe', }

expected_value = 'john@fullname.com'

empty_values = {'fullname':None, }

schema = Schema(tuple(field_instances))
sampleDisplayList = DisplayList([('e1', 'e1'), ('element2', 'element2')])

DummyVocabFactory = DummyVocabulary()

class TestFullnameField(FullnameFieldTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Fullname', 'fullname', title='Test Fullname Object')
        self._dummy = self.portal._getOb('fullname')
        m = self.portal.portal_membership.getAuthenticatedMember()
        m.fullname = 'john@fullname.com'

    def makeDummy(self):
        return self._dummy

    def test_processing(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        dummy.REQUEST = request
        dummy.processForm(data=1)
        value = dummy.getField('fullname').get(dummy)
        self.assertEquals(value, expected_value, 'got: %r, expected: %r' %
                            (value, expected_value))

    def test_defaults(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        field =  dummy.getField('fullname')

        self.failUnlessEqual(field.getDefault(dummy), 'John Doe')

        m = self.portal.portal_membership.getAuthenticatedMember()
        m.fullname = 'Mary Doe'
        self.failUnlessEqual(field.getDefault(dummy), 'Mary Doe')
        


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFullnameField))
    return suite

