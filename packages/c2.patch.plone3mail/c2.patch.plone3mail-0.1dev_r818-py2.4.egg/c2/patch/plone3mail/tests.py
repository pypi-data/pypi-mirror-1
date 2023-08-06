
from email import message_from_string
import unittest

from zope.testing import doctestunit
from zope.component import testing
from zope.component import getSiteManager
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from AccessControl import Unauthorized
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost

ptc.setupPloneSite()

import c2.patch.plone3mail

member_id = 'new_member'

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             c2.patch.plone3mail)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.registration = self.portal.portal_registration
        self.portal.acl_users.userFolderAddUser("userid", "password",
                (), (), ())
        self.portal.acl_users._doAddGroup("groupid", ())

    def testMailPassword(self):
        # tests email sending for password emails
        # First install a fake mailhost utility
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})
        # Set the portal email info
        self.portal.setTitle('T\xc3\xa4st Portal')
        self.portal.email_from_name = 'T\xc3\xa4st Admin'
        self.portal.email_from_address = 'bar@baz.com'
        self.registration.mailPassword(member_id, self.app['REQUEST'])
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_string(str(mails.messages[0]))
        # We get an encoded subject
        self.assertEqual(msg['Subject'],
                         '=?utf-8?q?Password_reset_request?=')
        # Also a partially encoded from header
        self.assertEqual(msg['From'],
                         # '=?utf-8?q?T=C3=A4st_Admin?= <bar@baz.com>')
                         '=?utf-8?b?IlTDpHN0IEFkbWluIiA=?=<bar@baz.com>')
        self.assertEqual(msg['Content-Type'], 'text/plain; charset=utf-8')
        # And a Quoted Printable encoded body
        # print msg.get_payload()
        # self.failUnless('T=C3=A4st Porta' in msg.get_payload())


    def testRegisteredNotify(self):
        # tests email sending on registration
        # First install a fake mailhost utility
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})
        # Set the portal email info
        self.portal.setTitle('T\xc3\xa4st Portal')
        self.portal.email_from_name = 'T\xc3\xa4st Admin'
        self.portal.email_from_address = 'bar@baz.com'
        self.registration.registeredNotify(member_id)
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_string(str(mails.messages[0]))
        # We get an encoded subject
        self.assertEqual(msg['Subject'],
                         '=?utf-8?q?User_Account_Information_for_T=C3=A4st_Portal?=')
        # Also a partially encoded from header
        self.assertEqual(msg['From'],
                         '=?utf-8?b?IlTDpHN0IEFkbWluIiA=?=<bar@baz.com>')
        self.assertEqual(msg['Content-Type'], 'text/plain; charset=utf-8')
        # And a Quoted Printable encoded body
        # self.failUnless('T=C3=A4st Admin' in msg.get_payload())

def test_suite():

    return unittest.TestSuite([
        unittest.makeSuite(TestCase)
        
        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='c2.patch.plone3mail',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='c2.patch.plone3mail.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='c2.patch.plone3mail',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='c2.patch.plone3mail',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
