__author__ = 'Fruch'

import os
import sys
import Queue
import threading
import pickle
import operator
from datetime import datetime
import time

import cherrypy
from genshi.template import TemplateLoader

loader = TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'templates'),
    auto_reload=True
)

num_worker_threads = 5

def do_work(item):
    print item.type
    time.sleep(10)
    item.status = "Failed"
    
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
     
class Job(object):

    def __init__(self, type, background, filename):
        self.type = type
        self.data = filename.read()
        self.time = datetime.now()
        self.id = hex(hash(tuple([filename, self.time])))[2:]
        self.status = "Created"
        self.log = ""
        
    def __repr__(self):
        return '<%s %s %s>' % (type(self).__name__, str(self.time), self.status)

class FileDemo(object):
    def __init__(self, data):
        self.data = data
        
    def index(self, items=10):
        links = sorted(self.data.values(), key=operator.attrgetter('time'))
        
        tmpl = loader.load('index.html')
        stream = tmpl.generate(links=links, items=items)
        return stream.render('html', doctype='html')
    index.exposed = True

    def upload(self, cancel=False, **data): 
        if cherrypy.request.method == 'POST':
            if cancel:
                raise cherrypy.HTTPRedirect('/')
            # validate data
            if not data['filename'].file:
                raise cherrypy.HTTPError(400, "You must supply a file")
            print str(data['filename'].content_type)
            if not (str(data['filename'].content_type) == 'application/octet-stream'):
                raise cherrypy.HTTPError(400, "You must supply a json file")
            
            job = Job(**data)
            self.data[job.id] = job
            
            if data['background'] == "yes":
                q.put( job )
                raise cherrypy.HTTPRedirect('/')
            do_work( job )
            raise cherrypy.HTTPRedirect('/')

        tmpl = loader.load('submit.html')
        stream = tmpl.generate()
        return stream.render('html', doctype='html')
        
    upload.exposed = True
    def jobstat(self, job_id):
        job = self.data[job_id]
    
        tmpl = loader.load('job.html')
        stream = tmpl.generate(job=job)
        return stream.render('html', doctype='html')
        
    jobstat.exposed = True
    
def main(filename="server.db"):
    # load data from the pickle file, or initialize it to an empty list
    if os.path.exists(filename):
        fileobj = open(filename, 'rb')
        try:
            data = pickle.load(fileobj)
        finally:
            fileobj.close()
    else:
        data = {}

    def _save_data():
        # save data back to the pickle file
        fileobj = open(filename, 'wb')
        try:
            pickle.dump(data, fileobj)
        finally:
            fileobj.close()
    if hasattr(cherrypy.engine, 'subscribe'): # CherryPy >= 3.1
        cherrypy.engine.subscribe('stop', _save_data)
    else:
        cherrypy.engine.on_stop_engine_list.append(_save_data)

    # Some global configuration; note that this could be moved into a
    # configuration file
    cherrypy.config.update({
        'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
        'tools.decode.on': True,
        'tools.trailing_slash.on': True,
        'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
    })

    cherrypy.quickstart(FileDemo(data), '/', {
        '/media': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    })

if __name__ == '__main__':
    main()