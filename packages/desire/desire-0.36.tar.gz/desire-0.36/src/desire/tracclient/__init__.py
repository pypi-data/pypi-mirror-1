import urllib
import urllib2
import re

class TracClient(object):
    
    def createTicket(self, ticketDefinition, tracConfiguration, sessionDetails):

        newTicketUrl = tracConfiguration.url + '/newticket'
        cookieHeader = 'trac_form_token=%s; kforge_auth=%s' % (
            sessionDetails.tracFormTokenCookie,
            sessionDetails.kforgeAuthCookie
        )
        headers = [('Cookie', cookieHeader)]


        postData = []
        postData.append(('__FORM_TOKEN', sessionDetails.tracFormTokenCookie))
        postData.append(('summary', ticketDefinition['summary']))
        postData.append(('type', 'enhancement'))
        postData.append(('description', ticketDefinition['description']))
        postData.append(('action','create'))
        postData.append(('status','new'))
        postData.append(('priority','major'))
        postData.append(('milestone',''))
        postData.append(('component','component1'))
        postData.append(('version',''))
        postData.append(('keywords',''))
        postData.append(('owner',''))
        postData.append(('cc',''))
        postData.append(('cost',ticketDefinition['cost']))
        postData.append(('actual_cost',''))
        postData.append(('value',ticketDefinition['value']))
                        
        response = self.makeRequest(newTicketUrl, headers, postData)

        if response.status != 302:
            raise Exception("Expected redirect on successful ticket submission, but got status code %s" % response.status)
        
        ticketUrl = response.getheader('Location')
        return ticketUrl

    def getFormToken(self, tracConfiguration, sessionDetails):
        response = self.makeRequest(tracConfiguration.url + '/newticket',
                                    [('Cookie', sessionDetails.cookieHeader())],
                                    None)
        possibleCookie = self.cookiesSetByResponse(response)
        if possibleCookie:
            (cookieName, cookieValue) = possibleCookie
            if cookieName == 'trac_form_token':
                sessionDetails.tracFormTokenCookie = cookieValue

    def cookiesSetByResponse(self, response):
        setCookieHeader = response.getheader('Set-Cookie')
        tokenRE = '[^\x00-\x1f\x7f()<>@,;:\\\\/\[\]?={}" \t]+'
        matches = re.search('^(' + tokenRE + ')=([^;]+)', setCookieHeader)
        if matches:
            return (matches.group(1), matches.group(2))
        return None
        
    def authenticate(self, tracConfiguration, userName, password):
        postVars = (
            ('name', userName),
            ('password', password),
            ('submit', 'Log in'),
            ('returnPath', '')
            )
        
        response = self.makeRequest(tracConfiguration.authUrl,
                                    [],
                                    urllib.urlencode(postVars)
                                    )
        cookie = response.getheader('Set-Cookie')
        if not cookie:
            return None
        
        matches = re.search('kforge_auth=([^;]+); ', cookie)
        if matches:
            return TracSession(None, matches.group(1))

        return None
        
    def makeRequest(self, url, headers, data=None):
        opener = urllib2.build_opener()
        opener.addheaders = headers
        
        if data:
            encodedData = urllib.urlencode(data) 
        else:
            encodedData = None
        return opener.open(url, encodedData)


class TracSession(object):

    def __init__(self, tracFormTokenCookie=None, kforgeAuthCookie=None):
        self.tracFormTokenCookie = tracFormTokenCookie
        self.kforgeAuthCookie = kforgeAuthCookie

    def cookieHeader(self):
        cookies = []
        
        if self.kforgeAuthCookie:
            cookies.append("kforge_auth=%s" % self.kforgeAuthCookie)
            
        if self.tracFormTokenCookie:
            cookies.append("trac_form_token=%s" % self.tracFormTokenCookie)

        return "; ".join(cookies)

class TracConfiguration(object):

    def __init__(self, mode, url, authUrl=None):
        self.mode = mode
        self.url = url
        self.authUrl = authUrl

