import httplib
import socket
import codecs
import urllib
import urllib2
import mechanize
import base64
import os
from xml.sax.saxutils import escape

from AccessControl import Unauthorized
from zope.component import getUtility

from collective.gsa.utils import encode_multipart_formdata, safe_unicode, make_cookie
from collective.gsa.interfaces import IGSAQueue
from collective.gsa.config import LIMIT
from logging import getLogger


logger = getLogger(__name__)

XML_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE gsafeed PUBLIC "-//Google//DTD GSA Feeds//EN" "">
<gsafeed>
    <header>
        <datasource>%s</datasource>
        <feedtype>incremental</feedtype>
    </header>
    <group>%s</group>
</gsafeed>
"""

class GSAException(Exception):
    """ An exception thrown by gsa connections """

    def __init__(self, httpcode, reason=None, body=None):
        self.httpcode = httpcode
        self.reason = reason
        self.body = body

    def __repr__(self):
        return 'HTTP code=%s, Reason=%s, body=%s' % (
                    self.httpcode, self.reason, self.body)

    def __str__(self):
        return 'HTTP code=%s, reason=%s' % (self.httpcode, self.reason)


class GSAConnection:

    def __init__(self, host='', port = None, source = '', postHeaders={}, \
                secure = False, timeout = None, only_public = False, request = None, dual_site = None):
        self.host = host
        self.port = port
        self.source = source
        self.encoder = codecs.getencoder('utf-8')
        self.timeout = timeout or None
        self.only_public = only_public
        self.dual_site = dual_site
        # responses from GSA will always be in UTF-8
        self.decoder = codecs.getdecoder('utf-8')  
        #self.toindex = {}
        self.xmlbody = []
        self.xmlheaders = {}
        self.xmlheaders.update(postHeaders)
        self.request = request
        # Prepare connection
        if secure:
            self.url = "https://%s:%s" % (host, port)
        else:
            self.url = "http://%s:%s" % (host, port)

        self.queue = getUtility(IGSAQueue)
        
        
    def __str__(self):
        return 'GSAConnection{host=%s, postHeaders=%s}' % \
            (self.host, self.xmlheaders)

    def login(self, username, password):
        """ Log into GSA and store GSA credential cookie 
        """
        logger.info('Logging in')
        
        password_mgr = mechanize.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.url, username, password)
        
        handler = mechanize.HTTPBasicAuthHandler(password_mgr)
        opener = mechanize.build_opener(handler)
        req = mechanize.Request('%s/search?access=a' % self.encoder(self.url)[0])

        # to speed thinks up - google won't check if cookies are enabled
        req.add_header('Cookie', 'COOKIETEST=1')
        
        try:
            res = opener.open(req)
        except urllib2.HTTPError, e:
            logger.warning('Login failed. The server couldn\'t fulfill the request. Error code: %s' % e.code)
            self.request.RESPONSE.setCookie('GSACookie', base64.b64encode('Unauthorized'))
            
        except urllib2.URLError, e:
            logger.warning('Login failed. We failed to reach a server. Reason: %s ' % e.reason)
        else:
            # get the cookie
            cj = mechanize.CookieJar()
            cj.extract_cookies(res,req)
            cookies = cj.cookies_for_request(req)
            cookie_ids = [x for x in cookies if x.name=='GSA_SESSION_ID']
            if len(cookie_ids) == 1:
                cookie = cookie_ids[0]
                cookie_str = mechanize.lwp_cookie_str(cookie)
                self.request.RESPONSE.setCookie('GSACookie', base64.b64encode(cookie_str))

            res.close()

    def getCredentialsCookie(self):
        cookie_str = base64.b64decode(self.request.cookies.get('GSACookie',''))
        cookie = None
        try:
            cookie = make_cookie(cookie_str)
        except AttributeError:
            pass
            
        return cookie

    def __errcheck(self,rsp):
        if rsp.code != 200:
            if rsp.code == 401:
                raise Unauthorized, "You are not authorized for GSA secure search"
                
            ex = GSAException(rsp.code, rsp.msg)
            try:
                ex.body = rsp.read()
            except:
                pass
            raise ex
        return rsp

    def doPost(self,body,headers):
        request = mechanize.Request('%s/xmlfeed' % self.encoder(self.url)[0], self.encoder(body)[0], headers)
        return self.sendRequest(request)
            
    def doGet(self,url):
        request = mechanize.Request("%s%s" % (self.encoder(self.url)[0], self.encoder(url)[0]))
        request = self.addCredentials(request)
        return self.sendRequest(request)
            
    def addCredentials(self, request):
        # Add credential cookie
        cj = mechanize.CookieJar()
        cookie = self.getCredentialsCookie()
        if cookie:
            cj.set_cookie(cookie)
            cj.add_cookie_header(request)
        return request
            
    def sendRequest(self, request):
        data = None
        try:
            res = mechanize.urlopen(request)
            res = self.__errcheck(res)
            data = res.read()
            res.fp._sock.recv = None
            res.close()
            del res
            del request
        except urllib2.HTTPError, e:
            logger.warning('The server couldn\'t fulfill the request. Error code: %s' % e.code)
        except urllib2.URLError, e:
            logger.warning('We failed to reach a server. Reason: %s ' % e.reason)
        except GSAException, e:
            logger.warning('The request failed. Reason: %s ' % str(e))
        
        return data
        
    def add(self, **data):
        # if it is already in there, just update
        row_dict = dict(
            url = safe_unicode(urllib.unquote(data['url'])),
            path = safe_unicode(urllib.unquote(data['path'])),
            action = u'add',
            mimetype = safe_unicode(data['mimetype']),
            modified = safe_unicode(data['last-modified']),
            content = (safe_unicode(data['content']), data.get('content_encoding')),
            metadata = data['metadata']
        )
        
        if data.get('authmethod'):
            row_dict['authmethod'] = data['authmethod']

        #self.toindex[data['url']] = row_dict
        
        self.queue.put(data['url'], row_dict)
        if len(self.queue) >= LIMIT:
            self.commit()

    def delete(self, **data):
        row_dict = dict(
            url = safe_unicode(data['url']),
            path = safe_unicode(data['path']),
            action = u'delete'
        )
        
        #self.toindex[data['url']] = row_dict
        self.queue.put(data['url'], row_dict)
        
        
    def search(self, **params):
        request = urllib.urlencode(params, doseq=True)
        if self.only_public:
            access = 'p'
        else:
            access = self.getCredentialsCookie() and 'a' or 'p'
            
        url = u'%s&output=xml_no_dtd&getfields=*&ie=utf8&oe=utf8&filter=0&access=%s' % (safe_unicode(params['q']), access)
        # TODO: better escaping
        url = u'/search?%s' % url.replace(' ','+')
        logger.info('Searing: %s' % url)
        response = self.doGet(url)
        return response

    def getRecordXML(self, row, dual = False):
        url = row['url']
        if dual:
            url = "%s%s" % (self.dual_site,row['path'])
            
        if row['action'] == 'delete':
            txt = u"<record url=\"%s\" action=\"%s\" />" % (url, row['action'])
            return txt
        
        txt = u"<record url=\"%s\" action=\"%s\" mimetype=\"%s\" last-modified=\"%s\" authmethod=\"%s\">" \
                % (url, row['action'], row['mimetype'], row['modified'], row['authmethod'])
        mt_data = row.get('metadata',{})
        if mt_data:
            txt += u"<metadata>"
            for name, value in mt_data.items():
                txt += u"<meta name=\"%s\" content=\"%s\"/>" % (safe_unicode(name), escape(safe_unicode(value), {'"':'&quot;'}))
            txt += u"</metadata>"
        content = row.get('content')
        if content:
            enc = content[1] and u"encoding=\"%s\"" % safe_unicode(content[1]) or u""
            cnt = content[0].startswith('<![CDATA') and safe_unicode(content[0]) or escape(safe_unicode(content[0]), {'"':'&quot;'})
            txt += u"<content %s>%s</content>" % (enc, cnt)
        txt += u"</record>"
        return txt
        
    def prepareXML(self):
        queue = self.queue
        
        records = ""
        log = ""
        count = 0
        processing = {}
        while count < LIMIT and len(queue) > 0:
            url, item = queue.get()
            processing[url] = item
            log += '    %s, action: %s\n' % (item['url'], item['action'])
            records += u"%s\n" % self.getRecordXML(item)
            if self.dual_site:
                records += u"%s\n" % self.getRecordXML(item, dual = True)
                
            count += 1
            if count > LIMIT:
                break
        
        logger.info('Reindexing: %s objects' % count)
        logger.debug('Reindexing: \n%s' % log)
        
        xml = XML_TEMPLATE % (self.source.encode('utf-8'),records)
        #logger.info(xml)
        return xml, processing
        
    def commit(self):
        queue = self.queue
        
        while len(queue) > 0:
            xml, processing = self.prepareXML()
            
            if 0:
                i = 1
                filename = "/tmp/gsafeed_%s.xml"

                while os.path.exists(filename % i):
                    i = i + 1

                filename = filename % i
                ff = open(filename, 'w')
                ff.write(self.encoder(xml)[0])
                ff.close()
            
            result = self.doSend(xml)
            if not result:
                # if failed, save the processing rows back
                logger.warning('Commit failed - not sent: %s requests' % len(processing))
                queue.update(processing)
                processing = None
                break
            
            processing.clear()
            del processing
                
    def doSend(self, xml):
        feedtype = u'incremental'
        datasource = safe_unicode(self.source)
        params = []
                
        params.append(("feedtype", feedtype))
        params.append(("datasource", datasource))    
        data=('data','xmlfilename',xml)
        
        content_type, body = encode_multipart_formdata(params, (data,))
        
        headers = self.xmlheaders
        headers['Content-type']=content_type.encode('utf-8')
        #headers['Content-length']=str(len(body.encode('utf-8')))
        
        result = self.doPost(body, headers)
        # the exception was raised
        if result is None:
            logger.error('Failed to send request')
            return False
        del data
        del result
        del xml
        return True
        
    def abort(self):
        pass