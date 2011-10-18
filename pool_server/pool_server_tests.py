# -*- coding: utf-8 -*-
"""
    Resource Pool Tests
    ~~~~~~~~~~~~~~

    Tests the Resource Pool application.

    :copyright: (c) 2011 by Israel Fruchter.
    :license: BSD, see LICENSE for more details.
"""
import json
import unittest
import pool_server
from ResourcePool import ObjectPool

class ResourcePoolTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Before each test, set up a blank database in memory"""
        pool_server.pool= ObjectPool("sqlite:///:memory:")
        pool = pool_server.pool
        pool.emptyAllResources()
        cls.app = pool_server.app.test_client()

    def add_resource(self, data, expected='Resources Added'):
        """ Add a Resource """
        for k, v in data.items():
            data["Resource--"+k] = v

        rv = self.app.post('/add', data=data,
                           follow_redirects=True)
        if data:
            self.assertIn(expected, rv.data)
        return rv

    def edit_resource(self, id, data):
        """ Edit a Resource """
        for k, v in data.items():
            data["Resource--"+k] = v

        rv = self.app.post('/edit/%s' % id, data=data,
                           follow_redirects=True)
        print rv.data
        if data:
            self.assertIn('Resources Edited', rv.data)
        return rv

    def retrieve_resource(self, type, data=None):
        """Retrieve a resource"""
        return json.loads( self.app.post('/retrieve/%s' % type, data=data,
                           follow_redirects=True).data )

    def return_resource(self, id):
        """Return a resource"""
        rv = self.app.get('/return/%s' % id,
                           follow_redirects=True)
        if id:
            assert "Resource Returned" in rv.data
        return rv

    def delete_resource(self, id):
        """delete a resource"""
        rv = self.app.get('/delete/%s' % id,
                           follow_redirects=True)
        if id:
            assert "Resource Deleted" in rv.data
        return rv

    def test_01_adding_resources(self):
        """ Test that resources can be added"""
        self.add_resource( dict(type="UPC", ip_address="10.62.24.1") )
        self.add_resource( dict(type="GPVR", ip_address="10.62.24.2") )
        self.add_resource( dict(type="UPC", ip_address="10.62.24.4") )
        self.add_resource( dict(type="UPC", ip_address="10.62.24.5") )
        self.add_resource( dict(type="UPC", ip_address="10.62.24.6") )
        self.add_resource( dict(type="UPC", ip_address="10.62.24.7") )
        self.add_resource( dict(type="UPC", ip_address="10.62.24.8") )

    def test_02_retrieve(self):
        """ Test that resource can be retrieved """
        res = self.retrieve_resource("UPC")
        self.assertEqual(res['ip_address'], "10.62.24.1")
        self.assertEqual(res['id'], 1)

        res = self.retrieve_resource("GPVR")
        self.assertEqual(res['ip_address'], "10.62.24.2")
        self.assertEqual(res['id'], 2)

    def test_03_return(self):
        res = self.retrieve_resource("UPC")
        self.assertEqual(res['ip_address'], "10.62.24.4")
        self.assertEqual(res['id'], 3)

        res = self.return_resource(res['id'])

        res = self.retrieve_resource("UPC")
        self.assertEqual(res['ip_address'], "10.62.24.4")
        self.assertEqual(res['id'], 3)

    def test_04_delete(self):
        res = self.retrieve_resource("UPC")
        self.assertEqual(res['ip_address'], "10.62.24.5")
        self.assertEqual(res['id'], 4)
        res = self.delete_resource(res['id'])

        #make sure it's deleted
        rv = self.app.get('/',
                   follow_redirects=True)
        self.assertNotIn("10.62.24.5", rv.data)

    def test_05_resource_list(self):
        rv = self.app.get('/',
                   follow_redirects=True)
        self.assertIn("10.62.24.6", rv.data)
        
    def test_06_edit(self):
        res = self.retrieve_resource("UPC")
        self.edit_resource(res['id'], dict(type="UPC", ip_address="192.168.1.1"))

        #make sure it's edited
        rv = self.app.get('/',
                   follow_redirects=True)
        self.assertNotIn("192.168.1.1", rv.data)
        
    def test_07_add_form(self):
        rv = self.app.get('/add',
                   follow_redirects=True)
        self.assertIn('<input type=submit value="Add">', rv.data)

    def test_08_platform_list(self):
        rv = json.loads(self.app.get('/platform_list',
                   follow_redirects=True).data)
        self.assertEquals({'platforms': ['UPC', 'GPVR']}, rv)

    def test_09_illegal_ip_address(self):
        self.add_resource( dict(type="UPC", ip_address="10.62.*") ,
                           expected="Not a valid IP or hostname address" )
        
    def test_10_illegal_mac_address(self):
        self.add_resource( dict(type="UPC", ip_address="10.62.23.32", mac_address="00:cc:22:ax:44:22") ,
                           expected="Not a valid MAC address" )

    def test_11_taken_by(self):
        res = self.retrieve_resource("UPC", data=dict(taken_by="fruch"))
        rv = self.app.get('/',
                   follow_redirects=True)
        self.assertIn("fruch", rv.data)
    
import unittest
import sys
import os.path
import subprocess
import threading
from ResourcePool import ObjectPool

class ExternalPoolTests(unittest.TestCase):
    curl_exec = os.path.join( os.path.dirname(os.path.abspath(__file__ )) , "curl")

    def python_piped_json_cmd(self, param):
        """ command line to read json from pipe """
        return '| ' + sys.executable + ' -c "import sys,json;\
                print json.loads(sys.stdin.read())[sys.argv[1]];\
                sys.exit(0)" %s' % param

    @classmethod
    def setUpClass(cls):
        # setup a clean test db
        pool_server.pool = ObjectPool('sqlite:///test.db?check_same_thread=False')
        pool_server.pool.emptyAllResources()

        # start the server in the background
        cls.t = threading.Thread(target=pool_server.app.run, args=['0.0.0.0', 1234, False])
        cls.t.daemon = True
        cls.t.start()

    def add_resource(self,type, ip_address):
        """ Add resources by type and ip_address """
        curl_params = '-L\
        --form-string "Resource--type=%s"\
        --form-string "Resource--ip_address=%s"\
        localhost:1234/add' % (type, ip_address)
        test = " ".join( (self.curl_exec , curl_params ))
        print test
        a = subprocess.check_output(test, shell=True)
        self.assertIn(ip_address, a)

    def test_00_add_resources(self):
        self.add_resource("UPC", "10.63.10.66")
        self.add_resource("GPVR", "10.63.10.63")

    def test_01_start(self):
        curl_params =  '-H "Accept: application/json" '
        curl_params += 'localhost:1234/retrieve/UPC'
        test = " ".join(
            (self.curl_exec , curl_params, self.python_piped_json_cmd("id"))
        )
        a = subprocess.check_output(test, shell=True)
        self.assertEqual(a, "1\n")

    def test_02_not_found(self):
        curl_params =  '-H "Accept: application/json" '
        curl_params += 'localhost:1234/retrieve/UPC'
        test = " ".join(
            (self.curl_exec , curl_params, self.python_piped_json_cmd("id"))
        )
        a = subprocess.check_output(test, shell=True)
        self.assertEqual(a, "None\n")

    def test_03_return_resource(self):
        curl_params = ' -L localhost:1234/return/1 '
        test = " ".join( (self.curl_exec , curl_params) )
        a = subprocess.check_output(test, shell=True)

        # now can retake the resource
        curl_params = '-H "Accept: application/json" '
        curl_params += '"localhost:1234/retrieve/UPC"'
        test = " ".join(
            (self.curl_exec , curl_params, self.python_piped_json_cmd("id"))
        )
        a = subprocess.check_output(test, shell=True)
        self.assertEqual(a, "1\n")
