#TODO: swith to restclient http://code.google.com/p/microapps/
from restful_lib import Connection

import xml.dom.minidom

# Should also work with https protocols
base_url = "http://127.0.0.1:8080"

conn = Connection(base_url, username="admin", password="a@123456")

def xml_2_list_dic(dom, item_string):
	def getText(nodelist):
		rc = ""
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc = rc + node.data
		return rc
	ret_list = []
	todos = dom.getElementsByTagName(item_string)
	for todo in todos:
		curr_dict = {}
		props = [x for x in todo.childNodes if not x.nodeType == x.TEXT_NODE]
		for node in props:
			curr_dict[node.nodeName] = getText(node.childNodes)
		ret_list.append(curr_dict)
	return ret_list
	
def get_projects():
	temp = conn.request_get("/projects.xml")
	mydom = xml.dom.minidom.parseString(temp['body'])
	return xml_2_list_dic(mydom, "project")
	
def get_contexts():
	temp = conn.request_get("/contexts.xml")
	mydom = xml.dom.minidom.parseString(temp['body'])
	return xml_2_list_dic(mydom, "context")
	
project_list = get_projects()

names = 'Projects: \n' + ''.join(["%s. %s\n" % (str(i+1),x['name']) for i, x in enumerate(project_list)])
print names

context_list = get_contexts()
names = 'Contexts: \n' + ''.join(["%s. %s\n" % (str(i+1),x['name']) for i, x in enumerate(context_list)])
print names