import sys
import time
import urllib2
import json

base_url="http://localhost:1234/resource/"
def http_request(path):
    req  = urllib2.Request(base_url + path)
    req.add_header('Accept', 'application/json')
    r = urllib2.urlopen(req).read()
    return json.loads(r)

def getResource(type, timeout=10, id=None):
    if timeout is None:
        timeout = sys.maxint
    for i in xrange(timeout/5):
        req = http_request("get/%s" % type)
        if req['id'] is not None:
            return req
        time.sleep(5)
    raise Exception("timeout expired")

def returnResource(id):
    return http_request("return/%s" % id)


GW = getResource("UPC")
print GW
CLIENT = getResource("GPVR")
print CLIENT
print returnResource(GW['id'])
print returnResource(CLIENT['id'])
