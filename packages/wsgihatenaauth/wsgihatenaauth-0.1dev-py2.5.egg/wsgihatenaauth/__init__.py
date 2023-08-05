# 
# Copyright (c) 2007, Atsushi Odagiri

# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" WSGI middleware for Hatena Auth
"""
import md5
import base64
import re
import urllib
import urllib2
import simplejson
from Crypto.Cipher import AES

certUrl = "http://auth.hatena.ne.jp/auth?api_key=%s&api_sig=%s"
authUrl = "http://auth.hatena.ne.jp/api/auth.json?api_key=%s&cert=%s&api_sig=%s"


class HatenaAuthHandler (object):
    def __init__(self, apiKey, secret):
        self.app = None
        self.apiKey = apiKey
        self.secret = secret
        self.certedUrl = "/auth"
        self.authenvkey = "REMOTE_USER"

    def redirectToHatenaAuth(self, environment, start_response):
        start_response("302 Moved Temporarily",
                       [("Location", self.getLoginUrl())])
        return []
                       
    def parseCookies(self, s):
        cookies = {}
        for x in [t.strip() for t in s.replace(",", ":").split(":")]:
            if x == "":
                continue
            key,value = x.split("=", 1)
            cookies[key] = value
        return cookies

    def __call__(self, app):
        self.app = app
        return self.handle

    def handle(self, environment, start_response):
        cookies = self.parseCookies(environment.get("HTTP_COOKIE", ""))
        if "hatena_auth" not in cookies:
            if not self.isCerted(environment):
                return self.redirectToHatenaAuth(environment, start_response)
        
            cert = self.getCert(environment)
            auth = self.getCertedUser(cert)
            if auth["has_error"]:
                start_response("500 Internal Error", [])
                return ["500 Internal Error", 
                        "hatena auth errored",
                        auth["error"]["message"]]
            authname = "hatena:%s" % auth["user"]["name"]
            environment[self.authenvkey] = auth
            
            serialized = self.serializeHatenaAuth(authname + " " * (32 - len(authname)))
            
            start_response("302 Moved Temporarily",
                            [("Set-Cookie",
                              "hatena_auth=%s" % serialized),
                             ("Location","/")])

            return [simplejson.dumps(auth)]
        else:
            auth = self.deserializeHatenaAuth(cookies["hatena_auth"])
            environment[self.authenvkey] = auth
        return self.app(environment, start_response)

    def serializeHatenaAuth(self, auth):
        obj = AES.new('abcdefghijklmnop', AES.MODE_CBC)
        
        return base64.b64encode(obj.encrypt(auth + ' ' * (32 - len(auth))))


    def deserializeHatenaAuth(self, auth):
        obj = AES.new('abcdefghijklmnop', AES.MODE_CBC)
        return obj.decrypt(base64.b64decode(auth)).strip()

    def getCertedUser(self, cert):
        apiSig = self.createApiSignature(self.secret,
                                         {"api_key":self.apiKey,
                                          "cert":cert}) 
        apiKey = self.apiKey
        url = authUrl % (apiKey, cert, apiSig)
        print url
        res = urllib2.urlopen(url)
        auth = simplejson.loads(res.read())
        return auth

    def createApiSignature(self, secret, params):
        paramKeys = params.keys()
        paramKeys.sort()
        paramStrs = []
        for key in paramKeys:
            paramStrs.append(key)
            paramStrs.append(params[key])
        print secret + "".join(paramStrs)
        m = md5.new()
        m.update(secret + "".join(paramStrs))
        sig = m.hexdigest()

        return sig

    
    def getLoginUrl(self):
        apiKey = self.apiKey
        secret = self.secret
        api_sig = self.createApiSignature(secret, {"api_key":apiKey})
        return certUrl % (apiKey, api_sig)
    

    def isCerted(self, environment):
        print environment["PATH_INFO"]
        return environment["PATH_INFO"] == self.certedUrl and environment["QUERY_STRING"].startswith("cert=")

    def getCert(self, environment):
        r = re.compile(r'^cert=(?P<cert>\w+)')
        m = r.match(environment["QUERY_STRING"])
        if m is None:
            return None
        return m.group("cert")

