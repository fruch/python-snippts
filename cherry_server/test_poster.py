# test_client.py
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

# Register the streaming http handlers with urllib2
register_openers()

# headers contains the necessary Content-Type and Content-Length
# datagen is a generator object that yields the encoded parameters
datagen, headers = multipart_encode({"myFile": open("run_pylint.py", "rb"), "background": "True"})

# Create the Request object
request = urllib2.Request("http://localhost:8080/upload", datagen, headers)
# Actually do the request, and get the response
print urllib2.urlopen(request).read()