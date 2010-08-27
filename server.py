from bottle  import route, request, run
from urllib2 import urlopen
from hashlib import sha1
from sys     import argv
from socket  import gethostname, gethostbyname
	
@route('/set/:key/:value')
def setroute(key, value):
	try:
		data[sha1(key)] = value
		return 'success'
	except:
		return 'failure'

@route('/get/:key')
def getroute(key):
	try:
		return data[key]
	except:
		return 'failure'
		
@route('/exists/:key')
def existsroute(key):
	if key in data:
		return 'true'
	else:
		return 'false'
		
@route('/nodes')
def nodesroute():
	if nodes:
		return ' '.join(nodes)
	else:
		return ''
		
@route('/size')
def sizeroute():
	return str(int(partition[1], 16) - int(partition[0], 16))
	
@route('/split')
def splitroute():
	start = int(partition[0], 16)
	end   = int(partition[1], 16)
	middle = int((end - start) / 2) + start
	partition[1] = middle
	return '%d %d' % (middle + 1, end)

address = gethostbyname(gethostname())
data = {}
nodes = []
partition = ['0', '1461501637330902918203684832716283019655932542975'] # sha1 integer space

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
			max_size = size
	node = max_node

	url = urlopen('http://%s/split' % node)
	partitoin = url.read().split(' ')
	url.close()	

run(host=address, port=8080)
