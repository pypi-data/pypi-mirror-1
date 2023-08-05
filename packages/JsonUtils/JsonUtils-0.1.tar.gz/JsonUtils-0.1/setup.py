from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="JsonUtils",
      version="0.1",
      description="jsonutils, a JSON parser and JSON-RPC handler.",
      long_description="""\
jsonutils provides the modules "json" and "jsonrpc". json is a simple
JSON (JavaScript Object Notation) parser and writer.  jsonrpc uses json
to implement a JSON Remote Procedure Call handler.  jsonrpc take a
jsonrpc request from the argument list, parses it, and passes the
arguments on to the specified method.
""",
      author="Russell Moffitt",
      author_email="Russell.Moffitt@noaa.gov",
      url="http://atlas.nmfs.hawaii.edu",
      keywords='json jsonrpc, json-rpc, jsonutils, rpc, javascript, xml, webservice',
      license='GPL',
      packages=find_packages(exclude='tests'),
      install_requires=[],
      )


