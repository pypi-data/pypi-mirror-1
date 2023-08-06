#!/opt/local/bin/python2.5
# -*- coding: utf-8 -*-
# http://d.hatena.ne.jp/keyword/%A4%CF%A4%C6%A4%CA%A5%B0%A5%E9%A5%D5api
# http://rubyforge.org/projects/hatenaapigraph/
#

import base64
import random
import sha
import urllib2
import urllib
from datetime import date,datetime

import yaml

def __http_response(self, request, response):
    code, msg, hdrs = response.code, response.msg, response.info()
    
    if not (200 <= code < 300):
        response = self.parent.error(
            'http', request, response, code, msg, hdrs)

    return response

urllib2.HTTPErrorProcessor.http_response = __http_response

class WSSEHeader(urllib2.BaseHandler) :
    
    def __init__(self, userid, passwd):
        self.userid = userid
        self.passwd = passwd

    def get_nonce(self):
        private = str(random.random())
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        return '%s %s' % (timestamp, sha.new('%s:%s' % (timestamp, private)).hexdigest())

    def get_wsse(self):
        nonce = self.get_nonce()
        base64_encoded_nonce = base64.encodestring(nonce).replace('\n', '')
        now = datetime.now()
        post_creation_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        password_digest = base64.encodestring(sha.new(nonce + post_creation_time + self.passwd).digest()).replace('\n', '')
        return 'UsernameToken Username="%s", PasswordDigest="%s", Created="%s", Nonce="%s"' \
            % (self.userid, password_digest, post_creation_time, base64_encoded_nonce)

    def http_request(self,req):
        req.add_header('X-WSSE', self.get_wsse())
        return req

class HatenaGraph:
    
    GRAPH_API_URL = 'http://graph.hatena.ne.jp/api/'
    GRAPH_API_DATA_URI = GRAPH_API_URL + 'data'
    GRAPH_API_CONFIG_URI = GRAPH_API_URL + 'config'

    def __init__(self, userid, passwd):
        self.userid = userid
        self.passwd = passwd

        
    def get_data(self, graphname, userid=None):
        if userid is None:
            userid = self.userid
        params = {
            'graphname' : graphname,
            'type' : 'yaml',
            'username' : userid
            }
        opener = urllib2.build_opener( WSSEHeader(self.userid, self.passwd))
        params = urllib.urlencode(params)
        data = opener.open(self.GRAPH_API_DATA_URI+'?%s' % params)
        return yaml.load(data)

    def post_data(self, graphname, value, updatedate=date.today()):
        params = {
            'graphname' : graphname,
            'value' : value,
            'date' : updatedate.strftime('%Y-%m-%d')
            }
        params = urllib.urlencode(params)
        opener = urllib2.build_opener( WSSEHeader(self.userid, self.passwd))
        return opener.open(self.GRAPH_API_DATA_URI, params)

    def get_config(self, graphname, userid=None):
        params = {
            'graphname' : graphname,
            'type' : 'yaml',
            }
        opener = urllib2.build_opener( WSSEHeader(self.userid, self.passwd))
        params = urllib.urlencode(params)
        data = opener.open(self.GRAPH_API_CONFIG_URI+'?%s' % params)
        return yaml.load(data)

    def post_config(self, graphname, params):
        params['graphname'] = graphname
        params = urllib.urlencode(params)
        opener = urllib2.build_opener( WSSEHeader(self.userid, self.passwd))
        return opener.open(self.GRAPH_API_CONFIG_URI, params)
