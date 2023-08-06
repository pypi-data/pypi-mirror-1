import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
ptc.setupPloneSite()


import sc.base.memberdataexport

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', sc.base.memberdataexport)
    zcml.load_config('test.zcml', sc.base.memberdataexport.tests)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite(products=['sc.base.memberdataexport'],
                   extension_profiles=['sc.base.memberdataexport:default',
                                       'sc.base.memberdataexport:testing'])

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def tearDown(cls):
            pass
    
    def afterSetUp(self):
        ''' Creates user accounts
        '''
        
        site = self.portal
        
        self.loginAsPortalOwner()
        
        members = [
                   ('kirk',['Manager','Editor','Contributor','Member',],
                          {'username':'kirk',
                           'email':'kirk@starfleet.org',
                           'fullname':'James Tiberius Kirk',
                           'rank':'Captain',
                           'age':45}), 
                   ('spock',['Member',],
                          {'username':'spock',
                           'email':'spock@starfleet.org',
                           'fullname':'Spock',
                           'rank':'First Officer',
                           'age':145}), 
                   ('mccoy',['Member',],
                          {'username':'mccoy',
                           'email':'mccoy@starfleet.org',
                           'fullname':'Leonard Mccoy',
                           'rank':'Officer',
                           'age':50}), 
                   ('sulu',['Member',],
                          {'username':'sulu',
                           'email':'sulu@starfleet.org',
                           'fullname':'Hikaru Sulu',
                           'rank':'Lieutenant',
                           'age':44}), 
                   ('chekov',['Member',],
                          {'username':'chekov',
                           'email':'chekov@starfleet.org',
                           'fullname':'Pavel Andreievich Chekov',
                           'rank':'Lieutenant',
                           'age':35}), 
                   ('pike',['Member','Editor',],
                          {'username':'pike',
                           'email':'pike@starfleet.org',
                           'fullname':'Christopher Pike',
                           'rank':'Admiral',
                           'age':58}), 
                  ]
        for member_id, roles, properties in members:
            member_pwd = 'klingonEmpire'
            member = site.portal_registration.addMember(member_id, 
                                                        member_pwd,roles,
                                                        properties=properties)
    
    


def test_suite():
    return unittest.TestSuite([
        
        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='sc.base.memberdataexport',
        #    setUp=testing.setUp, tearDown=testing.tearDown),
        
        #doctestunit.DocTestSuite(
        #    module='sc.base.memberdataexport.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),
        
        
        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='sc.base.memberdataexport',
        #    test_class=TestCase),
        
        ztc.FunctionalDocFileSuite(
            'browser.txt', 
            package='sc.base.memberdataexport.docs',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | 
                        doctest.NORMALIZE_WHITESPACE | 
                        doctest.ELLIPSIS,
            test_class=TestCase),
            
        ])
        


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
