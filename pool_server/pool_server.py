__author__ = 'ifruchte'

import web
import json
from mimerender import mimerender

from ResourcePool import Resource, ObjectPool
import HTML

render_json = lambda **args: json.dumps(args)
render_txt = lambda message: message

urls = (
    '/resource/get/(.*)', 'resource_get',
    '/resource/return/(.*)', 'resource_return',
    '/resource/list', 'resource_list'
)
app = web.application(urls, globals(), autoreload=True)
pool = ObjectPool()

def as_dict(obj):
    res = {}
    for col in Resource.__table__.c:
        res[col.key] = getattr(obj ,col.key)
    return res

class resource_get:
    @mimerender(
        default = 'json',
        json = lambda **args: json.dumps(args),
        txt  = lambda id, message: "%s : %s"% (id, message)
    )
    def GET(self, type):
        try:
            ret = as_dict(pool.getResource(type))
        except Exception as e:
            ret = dict(message=e.message, id=None)
        return ret

class resource_return:
    @mimerender(
        default = 'json',
        json = render_json,
        txt  = render_txt
    )
    def GET(self, id):
        a = pool.returnResource(id=id)
        return {'message': "%s returned OK!" % id}

class resource_list:
    def GET(self):
        keys = []
        for c in Resource.__table__.c:
            keys += [c.key]
        t = HTML.Table(header_row=keys)

        for r in pool.allResourcesGenerator():
            t.rows.append([r.__dict__[key] for key in keys])

        return str(t)
    
if __name__ == "__main__":
    app.run()

import unittest
import sys
import subprocess
import threading

class PoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pool.emptyAllResources()
        try:
            pool.addResource(Resource("UPC", "10.64.62.111"))
            pool.addResource(Resource("GPVR", "10.64.62.23"))
        except IntegrityError:
            pass

        sys.argv[1] = "1234"
        cls.t = threading.Thread( target=app.run)
        cls.t.daemon = True
        cls.t.start()

    def test_01_start(self):
        curl_exec = "c:\pylogsparser\curl"
        curl_params = ' -H "Accept: application/json" localhost:1234/resource/get/UPC'
        test = " ".join( (curl_exec , curl_params,
                          '| ',sys.executable,' -c "import sys,json;',
                          "print json.loads(sys.stdin.read())[sys.argv[1]];"
                          'sys.exit(0)" id') )
        print test
        a = subprocess.check_output(test, shell=True)
        self.assertEqual(a, "1\n")

    def test_02_not_found(self):
        curl_exec = "c:\pylogsparser\curl"
        curl_params = ' -H "Accept: application/json" localhost:1234/resource/get/UPC'
        test = " ".join( (curl_exec , curl_params,
                          '| ',sys.executable,' -c "import sys,json;',
                          "print json.loads(sys.stdin.read())[sys.argv[1]];"
                          'sys.exit(0)" id') )
        print test
        a = subprocess.check_output(test, shell=True)
        self.assertEqual(a, "None\n")

    def test_03_return_resource(self):
        curl_exec = "c:\pylogsparser\curl"
        curl_params = ' -H "Accept: application/json" localhost:1234/resource/return/1'
        test = " ".join( (curl_exec , curl_params,
                          '| ',sys.executable,' -c "import sys,json;',
                          "print json.loads(sys.stdin.read())[sys.argv[1]];"
                          'sys.exit(0)" message') )
        print test
        a = subprocess.check_output(test, shell=True)
        self.assertEqual(a, "1 returned OK!\n")

        # now can retake the resource
        curl_exec = "c:\pylogsparser\curl"
        curl_params = ' -H "Accept: application/json" localhost:1234/resource/get/UPC'
        test = " ".join( (curl_exec , curl_params,
                          '| ',sys.executable,' -c "import sys,json;',
                          "print json.loads(sys.stdin.read())[sys.argv[1]];"
                          'sys.exit(0)" id') )
        a = subprocess.check_output(test, shell=True)
        self.assertEqual(a, "1\n")
  