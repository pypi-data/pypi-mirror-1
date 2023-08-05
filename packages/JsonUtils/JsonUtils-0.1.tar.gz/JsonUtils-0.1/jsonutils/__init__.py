#Module jsontools
#  jsonrpc:  http based json-rpc handler that pulls requests from cgi 'get' or 'post' data
#  json:  read and write methods for serializing/unserializing json objects
__version__ = '1.0'

__all__ = ["json", "jsonrpc"]

try:
    import json
    import jsonrpc
except ImportError:
    pass
