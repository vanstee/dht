from bottle   import run, route, app, request, redirect
from urllib2  import urlopen
from urlparse import urlparse
from hashlib  import sha1
from sys      import argv
from socket   import gethostname, gethostbyname

data     = {}
keyspace = [0, 0xffffffffffffffffffffffffffffffffffffffff]
host     = gethostbyname(gethostname())
nodes    = set([host])
port     = '8080'

def join():
	global nodes, keyspace
	node = argv[1]
	url = urlopen('http://%s/nodes' % node)
	response = url.read()
	url.close()
	if response:
		nodes = set(response.split(' '))
	
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
	
	url = urlopen('http://%s/split' % node)
	keyspace = [int(i) for i in url.read().split(' ')]
	url.close()
		
@route('/set/:key/:value')
def setroute(key, value):
	hashkey = int(sha1(key).hexdigest(), 16)
	if hashkey >= keyspace[0] and hashkey <= keyspace[1]:
		data[hashkey] = value
		return 'success'
	else:
		for node in nodes:
			url = urlopen('http://%s/contains/%s' % (node, key))
			if bool(url.read()):
				redirect('http://%s/set/%s/%s' % (node, key, value))
		#raise Exception('missing node')
		return 'failure'

@route('/get/:key')
def getroute(key):
	hashkey = int(sha1(key).hexdigest(), 16)
	if hashkey >= keyspace[0] and hashkey <= keyspace[1]:
		if hashkey in data:	
			return data[hashkey]
		else:
			return 'failure'
	else:
		for node in nodes:
			url = urlopen('http://%s/contains/%s' % (node, key))
			if bool(url.read()):
				redirect('http://%s/get/%s/' % (node, key))
				break
		#raise Exception('missing node')
		return 'failure'
	
@route('/contains/:key')
def containsroute(key):
	hashkey = int(sha1(key).hexdigest(), 16)
	return str(hashkey >= keyspace[0] and hashkey <= keyspace[1]).lower()

@route('/nodes')
def nodesroute():
	return ' '.join(nodes)

@route('/size')
def sizeroute():
	nodes.add(request['REMOTE_ADDR'] + ':8080')
	return str(keyspace[1] - keyspace[0])

@route('/split')
def splitroute():
	start, end = keyspace
	keyspace[1] = int((start + end) / 2)
	return '%d %d' % (keyspace[1] + 1, end)

if len(argv) == 2:
	join()
	
app().catchall = False
run(host = host, port = port)