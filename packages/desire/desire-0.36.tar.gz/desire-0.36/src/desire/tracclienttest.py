import unittest
from desire.testunit import TestCase
from desire.tracclient import TracClient, TracConfiguration, TracSession
import httplib

def suite():
    suites = [
        unittest.makeSuite(TestTracClient),
    ]
    return unittest.TestSuite(suites)


class StubResponse(object):
    status = 200
    headers = {}
    
    def getheader(self, headerName):
        try:
            return self.headers[headerName]
        except:
            return None

class StubTracClient(TracClient):
    callsReceived = None
    response = None

    def __init__(self):
        self.callsReceived = {'makeRequest':[]}
        self.response = StubResponse()
        
    def makeRequest(self, url, headers, data=None):
        self.callsReceived['makeRequest'].append([url,headers,data])
        return self.response

class TestTracClient(TestCase):
    
    def setUp(self):
        self.tracConfiguration = TracConfiguration(
            mode='kforge',
            url='http://my.domain.com/trac',
            authUrl='http://kforge.my.domain.com/',
        )

    def tearDown(self):
        pass

    def test_authenticate(self):
        tracClient = StubTracClient()
        tracClient.response.headers = {
            'Set-Cookie':
            'kforge_auth=304658136ec5ccd3837dee379022dbb43eafd1d5ebbc2df153dbf4cd066096a1; Domain=.my.domain.com; Path=/;'
            }
        
        tracSessionDetails = tracClient.authenticate(self.tracConfiguration, "MyUser", "VerySecretPassword")
        expectedCall = ['http://kforge.my.domain.com/',
                        [],
                        'name=MyUser&password=VerySecretPassword&submit=Log+in&returnPath=']
        self.failUnlessEqual(tracClient.callsReceived['makeRequest'][0], expectedCall)
        self.failUnlessEqual(tracSessionDetails.kforgeAuthCookie,
                             '304658136ec5ccd3837dee379022dbb43eafd1d5ebbc2df153dbf4cd066096a1')
        self.failUnlessEqual(tracSessionDetails.tracFormTokenCookie,
                             None)
        
    def test_getFormToken(self):
        tracClient = StubTracClient()
        tracClient.response.headers = {
            'Set-Cookie':
            'trac_form_token=8d59b33588111454a2bba104; Path=/trac;'
            }
        
        tracSessionDetails = TracSession(None, '304658136ec5ccd3837dee379022dbb43eafd1d5ebbc2df153dbf4cd066096a1')
        tracClient.getFormToken(self.tracConfiguration, tracSessionDetails)
        expectedCall = ['http://my.domain.com/trac/newticket',
                        [('Cookie', 'kforge_auth=304658136ec5ccd3837dee379022dbb43eafd1d5ebbc2df153dbf4cd066096a1')],
                        None]
        self.failUnlessEqual(tracClient.callsReceived['makeRequest'][0], expectedCall)
        self.failUnlessEqual(tracSessionDetails.tracFormTokenCookie, '8d59b33588111454a2bba104')
        
    def test_createTicket(self):
        tracClient = StubTracClient()
        tracClient.response.status = 302
        tracClient.response.headers = {'Location': 'http://my.domain.com/trac/ticket/1234'}

        ticketDefinition = {
            'summary': 'test',
            'cost': '1',
            'value': '100',
            'description': 'This is the description',
        }

        sessionDetails = TracSession(
            tracFormTokenCookie='8d59b33588111454a2bba104',
            kforgeAuthCookie='8a4358965ad96dce402e5afc85e110b241c903c5da45d18f0e15a9cbe9f234d3',
        )
        
        ticketUrl = tracClient.createTicket(ticketDefinition, self.tracConfiguration, sessionDetails)

        expectedPostData = [
            ('__FORM_TOKEN', '8d59b33588111454a2bba104'),
            ('summary', 'test'),
            ('type', 'enhancement'),
            ('description', 'This is the description'),
            ('action','create'),
            ('status','new'),
            ('priority','major'),
            ('milestone',''),
            ('component','component1'),
            ('version',''),
            ('keywords',''),
            ('owner',''),
            ('cc',''),
            ('cost','1'),
            ('actual_cost',''),
            ('value','100')
        ]
        expectedCall = ['http://my.domain.com/trac/newticket',
                        [('Cookie', 'trac_form_token=8d59b33588111454a2bba104; kforge_auth=8a4358965ad96dce402e5afc85e110b241c903c5da45d18f0e15a9cbe9f234d3')],
                        expectedPostData
                        ]
        self.failUnlessEqual(tracClient.callsReceived['makeRequest'][0], expectedCall)
        self.failUnlessEqual(ticketUrl, 'http://my.domain.com/trac/ticket/1234')
        
