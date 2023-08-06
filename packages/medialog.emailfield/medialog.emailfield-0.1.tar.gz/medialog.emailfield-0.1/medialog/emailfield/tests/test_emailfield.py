from Products.Archetypes.atapi import *
from Products.Archetypes.tests.test_fields import FakeRequest
from Products.Archetypes.tests.test_fields import DummyVocabulary

from medialog.emailfield.field import EmailField 
from medialog.emailfield.tests.base import EmailFieldTestCase 


field_instances = [EmailField('emailfield')]

field_values = {'email':'john@email.com', }

expected_value = 'john@email.com'

empty_values = {'email':None, }

schema = Schema(tuple(field_instances))
sampleDisplayList = DisplayList([('e1', 'e1'), ('element2', 'element2')])

DummyVocabFactory = DummyVocabulary()

class TestEmailField(EmailFieldTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Email', 'email', title='Test Email Object')
        self._dummy = self.portal._getOb('email')
        m = self.portal.portal_membership.getAuthenticatedMember()
        m.email = 'john@email.com'

    def makeDummy(self):
        return self._dummy

    def test_processing(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update(field_values)
        dummy.REQUEST = request
        dummy.processForm(data=1)
        value = dummy.getField('email').get(dummy)
        self.assertEquals(value, expected_value, 'got: %r, expected: %r' %
                            (value, expected_value))

    def test_validation(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        request.form.update({'email':'xxx'})
        request.form['fieldset'] = 'default'
        dummy.REQUEST = request
        errors = dummy.validate()
        expected = {'email': u"Validation failed(isEmail): 'xxx' is not a valid email address."}
        self.failIf(errors, expected)

        request.form.update({'email':'xxx@mail.com'})
        request.form['fieldset'] = 'default'
        dummy.REQUEST = request
        errors = dummy.validate()
        self.failIf(errors, {})

    def test_defaults(self):
        dummy = self.makeDummy()
        request = FakeRequest()
        field =  dummy.getField('email')

        self.failUnlessEqual(field.getDefault(dummy), 'john@email.com')

        m = self.portal.portal_membership.getAuthenticatedMember()
        m.email = 'mary@email.com'
        self.failUnlessEqual(field.getDefault(dummy), 'mary@email.com')
        


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEmailField))
    return suite

