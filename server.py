from bottle  import route, request, run, app
from urllib2 import urlopen
from hashlib import sha1
from sys     import argv
from socket  import gethostname, gethostbyname
	
@route('/set/:key/:value')
def setroute(key, value):
	node = findnode(key)
	keyhash = int(sha1(key).hexdigest(), 16)
	if node == address:
		try:
			data[keyhash] = value
			print 'local key set success'
			return 'success'
		except:
			print 'local key set failure'
			return 'failure'
	else:
		try:
			url = urlopen('http://%s/set/%s/%s' % (node, key, value))
			response = url.read()
			url.close()
			print 'remote key set success'
			return response
		except:
			print 'remote key set failure'		
			return 'failure'

@route('/get/:key')
def getroute(key):
	node = findnode(key)
	keyhash = int(sha1(key).hexdigest(), 16)
	if node == address:
		try:
			if keyhash in data:			
				print 'local key get success'
				return data[keyhash]
			else:
				print 'local key get failure (missing key)'
				return 'failure'
		except:
			print 'local key get failure'
			return 'failure'
	else:
		try:
			url = urlopen('http://%s/get/%s' % (node, key))
			response = url.read()
			url.close()
			print 'remote key get success'
			return response
		except:
			print 'remote key get failure'
			return 'failure'
		
@route('/exists/:key')
def existsroute(key):
	node = findnode(key)
	keyhash = int(sha1(key).hexdigest(), 16)
	if node == address:
		try:
			if keyhash in data:
				print 'local key exists success'
				return 'success'
			else:
				print 'local key exists failure (missing key)'
				return 'failure'
		except:
			print 'local key exists failure'
			return 'failure'
	else:
		try:
			url = urlopen('http://%s/get/%s' % (node, key))
			response = url.read()
			url.close()
			print 'remote key exists success'
			return response
		except:
			print 'remote key exists failure'
			return 'failure'
		
@route('/nodes')
def nodesroute():
	if nodes:
		return ' '.join(nodes)
	else:
		return ''
		
@route('/size')
def sizeroute():
	return str(partition[1] - partition[0])
	
@route('/split')
def splitroute():
	start = partition[0]
	end   = partition[1]
	middle = ((end - start) / 2) + start
	partition[1] = middle
	return '%d %d' % (middle + 1, end)
	
@route('/contains/:key')
def containsroute(key):
	keyhash = int(sha1(key).hexdigest(), 16)
	start = partition[0]
	end   = partition[1]	
	if start >= keyhash or end <= keyhash:
		return 'true'
	else:
		return 'false'
		
def findnode(key):
	for node in nodes:
		try:
			url = urlopen('http://%s/contains/%s' % (node, key))
			response = url.read()
			print '%s %s' % (node, response)
			url.close()
			if bool(response):
				return node
		except:
			pass
	raise Exception('missing node')
	return

address = gethostbyname(gethostname())
data = {}
nodes = []
partition = [0x0L, 0xffffffffffffffffffffffffffffffffffffffffL] # sha1 space

if len(argv) == 2:
	node = argv[1]

	print 'http://%s/nodes' % node
	url = urlopen('http://%s/nodes' % node)
	response = url.read()
	url.close()
	if response:
		nodes = response.split(' ')
	nodes.append(node)

	max_node = nodes[0]
	max_size = sizeroute()
	for node in nodes:
		print 'http://%s/size' % node
		url = urlopen('http://%s/size' % node)
		node_size = url.read()
		url.close()
		if max_node > max_size:
			max_node = node
			max_size = node_size
	node = max_node

	url = urlopen('http://%s/split' % node)
	partition = url.read().split(' ')
	print partition
	url.close()	

app().catchall = False
run(host=address, port=8080)
