__author__ = 'Fruch'

import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

import cherrypy
import Queue
import threading

#TODO: add Genshi templates

num_worker_threads = 5

def do_work(item):
    print item['type']
    
def worker():
    while True:
        item = q.get()
        print 'doing work from worker'
        do_work(item)
        q.task_done()

q = Queue.Queue()
for i in range(num_worker_threads):
     t = threading.Thread(target=worker)
     t.daemon = True
     t.start()
     
class FileDemo(object):

    def index(self):
        return """
        <html><body>
        <style type="text/css">
        form{margin:0;padding:0;}fieldset{margin:1em 0;border:none;border-top:1px solid #ccc;}legend{margin:1em 0;padding:0 .5em;color:#036;background:transparent;font-size:1.3em;font-weight:bold;}label{float:left;width:100px;padding:0 1em;text-align:right;}fieldset div{margin-bottom:.5em;padding:0;display:block;}fieldset div input,fieldset div textarea{width:150px;border-top:1px solid #555;border-left:1px solid #555;border-bottom:1px solid #ccc;border-right:1px solid #ccc;padding:1px;color:#333;}fieldset div select{padding:1px;}div.fm-multi div{margin:5px 0;}div.fm-multi input{width:1em;}div.fm-multi label{display:block;width:200px;padding-left:5em;text-align:left;}#fm-submit{clear:both;padding-top:1em;text-align:left;}#fm-submit input{border:1px solid #333;padding:2px 1em;background:#555;color:#fff;font-size:100%;}input:focus,textarea:focus{background:#efefef;color:#000;}fieldset div.fm-req{font-weight:bold;}fieldset div.fm-req label:before{content:"* ";}body{padding:0;margin:20px;color:#333;background:#fff;font:12px arial,verdana,sans-serif;text-align:left;}#container{margin:0 auto;padding:1em;width:600px;text-align:left;}p#fm-intro{margin:0;}
        </style>
        <div id="container"> 
        <h2>Submit a test description .json into QC</h2>
            <form id="fm-form" action="upload" method="post" enctype="multipart/form-data">
                <div class="fm-req"> 
                  <label for="type">Type: </label> 
                  <select name="type" id="type" >
                  <option value="desc">Test Description</option>
                  <option value="results">Test Results</option>
                  </select>                  
                </div>
                <div class="fm-req"> 
                  <label for="myFile">Filename: </label> 
                  <input name="myFile" id="myFile" type="file" /> 
                </div>
                <div class="fm-multi"> 
                <div class="fm-opt"> <p>Run in background ?</p> 
                    <label for="background"> 
                    <input name="background" type="radio" id="fm-newsopt-yes" value="yes" checked="checked" /> 
                    Yes</label> 
                    <label for="fm-newsopt-no"> 
                        <input id="fm-newsopt-no" name="background" type="radio" value="no" /> 
                    No</label> 
                </div> 
                </div>
                <input type="submit" />
            </form>
        </div>
        </body></html>
        """
    index.exposed = True

    def upload(self, type, myFile, background="no"):
        out = """<html>
        <body>
            myFile length: %s<br />
            myFile filename: %s<br />
            myFile mime-type: %s
        </body>
        </html>"""
        if not myFile.file:
            raise cherrypy.HTTPError(400, "You must supply a file")
        print str(myFile.content_type)
        if not (str(myFile.content_type) == 'application/octet-stream'):
            raise cherrypy.HTTPError(400, "You must supply a json file")
            
        item = dict(type = type ,file=myFile.file.read())
        if background == "yes":
            q.put( item )
            return "will handle it in the background"
        # Although this just counts the file length, it demonstrates
        # how to read large files in chunks instead of all at once.
        # CherryPy reads the uploaded file into a temporary file;
        # myFile.file.read reads from that.
        size = 0
        do_work(item)
        myFile.file.seek(0)
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)
        
        return out % (size, myFile.filename, myFile.content_type)
    upload.exposed = True

cherrypy.quickstart(FileDemo())