import SimpleXMLRPCServer

class Queue:
	def __init__(self):
		self.queue = []

	def pop(self, index):
		try:
			return self.queue.pop(index)
		except IndexError:
			return ""

	def push(self, item):
		self.queue.append(item)
		return "ok"


def runserver(host='0.0.0.0', port=5656):
	server = SimpleXMLRPCServer.SimpleXMLRPCServer((host, port))
	server.register_introspection_functions()
	server.register_instance(Queue())
	server.serve_forever()
