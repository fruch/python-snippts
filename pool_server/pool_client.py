import sys
import time
import urllib2
import json

base_url="http://localhost:5000/"

def http_request(path):
    req  = urllib2.Request(base_url + path)
    req.add_header('Accept', 'application/json')
    r = urllib2.urlopen(req).read()
    return r

def retrieveResource(type, timeout=10, id=None):
    ''' Retrieve Resource with retry and timeout '''
    if timeout is None:
        timeout = sys.maxint
    for i in xrange(timeout/5):
        req = json.loads( http_request("retrieve/%s" % type) )
        if req['id'] is not None:
            return req
        time.sleep(5)
    raise Exception("timeout expired")

def returnResource(id):
    return http_request("return/%s" % id)


GW = retrieveResource("UPC")
print GW
CLIENT = retrieveResource("GPVR")
print CLIENT
print returnResource(GW['id'])
print returnResource(CLIENT['id'])
