import ConfigParser

config = ConfigParser.ConfigParser()
config.read('example.cfg')

real = dict()
list = config.items('PythonTool')
for (w,x) in list:
	print w +" -> "+ x
	real[w] = x
	

print list
print list[1]
print list[1] + list[3]
if 'foo' in real:
	print real['foo']
else:
	print "foo wasn't there"
print real