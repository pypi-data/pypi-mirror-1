#!/usr/bin/env python

import xmlrpclib

class QueueClient:
	def __init__(self, xmlrpc_url="http://localhost:5656"):
		self.server = xmlrpclib.Server(xmlrpc_url)

	def pop(self, index=0):
		return self.server.pop(index)

	def push(self, item):
		self.server.push(item)
