from bottle   import run, route, app, request, redirect
from urllib2  import urlopen
from urlparse import urlparse
from hashlib  import sha1
from sys      import argv
from socket   import gethostname, gethostbyname

data     = []
keyspace = [0, 128]
nodes    = set()
host     = gethostbyname(gethostname())

if len(argv) == 2:
	join()

def join():
	global nodes
	node = argv[1]
	url = urlopen('http://%s/nodes' % node)
	response = url.read()
	url.close()
	if response:
		nodes = set(response.split(' '))
	nodes.add(node)
	
	max_node = node
	url = urlopen('http://%s/size' % node)
	max_size = int(url.read())
	url.close()
	for node in nodes:
		url = urlopen('http://%s/size' % node)
		node_size = int(url.read())
		url.close()
		if node_size > max_size:
			max_node = node
			max_size = node_size
	node = max_node
	
	url = urlopen('http://%s/split')
	keyspace = url.read().split(' ')
	url.close()
		
@route('/set/:key/value')
def setroute(key, value):
	pass

@route('/get/:key')
def getroute(key):
	pass

@route('/nodes')
def nodesroute():
	return ' '.join(nodes)

@route('/size')
def sizeroute():
	nodes.add(urlparse(request.url).hostname)
	return keyspace[1] - keyspace[0]

@route('/split')
def splitroute():
	start, end = keyspace
	keyspace[1] = int((start + end) / 2)
	return '%d %d' % (keyspace[1] + 1, end)

app().catchall = False
run(host = host, port = 8080)
