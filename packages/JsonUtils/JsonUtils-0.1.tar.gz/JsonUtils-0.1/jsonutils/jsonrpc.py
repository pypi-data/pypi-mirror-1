__version__ = '1.0'

import json
import cgi, re, sys

##    jsonrpc.py takes JSON-RPC requests, passes them to the specified
##    method, and returns the result as a JSON-RPC message. 
##    Copyright (C) 2005  Russell A. Moffitt
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Lesser General Public
##    License as published by the Free Software Foundation.

textTemplate = """Content-Type: text/plain

%(content)s"""

NameAllowedRegExp=re.compile("^[a-zA-Z]\w*$")
def nameAllowed(name):
	"""checks if a name is allowed.
	"""
	if NameAllowedRegExp.match(name):
		return True
	else:
		return False

def getTracebackStr():
	import traceback
	import StringIO
	s=StringIO.StringIO("")
	traceback.print_exc(file=s)
	return s.getvalue()

class JSONRPCError:
	def __init__(self, msg=""):
		self.name = self.__class__.__name__
		self.msg = msg
class InvalidJsonRpcRequest(JSONRPCError):
	pass
class InvalidMethodParameters(JSONRPCError):
	pass
class MethodNotFound(JSONRPCError):
	pass
class ApplicationError(JSONRPCError):
	pass

class JsonRpcHandler:
	def __init__(self, services=None):
		"""Create RPC request/response handler for authorized methods listed in dictionary 'services'"""
		self.services = services or {}
	def getMethodByName(self, name):
		"""searches for an object with the name given inside the object given.
			"obj.child.meth" will return the meth obj.
		"""
		try:#to get a method by asking the service
			method = self.services._getMethodByName(name)
		except:
			#assumed a childObject is ment 
			for meth in self.services:
				if nameAllowed(name):
					method = self.services[name]
		return method
	def sendResponse(self, id, result, error):
		response = json.write({'id':id, 'result':result, 'error':error})
		print textTemplate % { 'content': response }
		#sys.exit()
	def handleJsonRpc(self):
		# Get parameter values from the "get" query string or "post" args
		fields = cgi.FieldStorage()
		request = fields.getfirst('request')
		try:
			if request == None:
				raise InvalidJsonRpcRequest
			req = json.read(request)
			id = req['id']
			params = req['params']
			methodname = req['method']
		except:
			self.sendResponse(None, None, InvalidJsonRpcRequest("Empty or malformed JSON-RPC request.").__dict__)
			return()
		try: #to get a callable obj 
			method = self.getMethodByName(methodname)
		except:
			method=None
			self.sendResponse(id, None, MethodNotFound(req['method']).__dict__)
			return()
		if method:
			try:
				result = method(*params)
				if (id is not None):
					self.sendResponse(id, result, None)
					return()
			except SystemExit: pass
			except: #error inside the callable object
				s=getTracebackStr()
				self.sendResponse(id, None, ApplicationError(s).__dict__)
				return()

if (__name__ == "__main__"):
	jsontxt = """request={
		"method": "foo",
		"params": ["spam", 321],
		"id": 1234
	}"""
	
	if (len(sys.argv) < 2):
		sys.argv.append(jsontxt)
	
	def foo(*args):
		return args
	
	services = {'foo':foo}
	myJson = JsonRpcHandler(services)
	myJson.handleJsonRpc()
