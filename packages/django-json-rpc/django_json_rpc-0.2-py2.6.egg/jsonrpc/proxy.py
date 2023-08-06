import urllib
import uuid
from json import dumps, loads
        
class ServiceProxy(object):
  def __init__(self, service_url, service_name=None, version='1.0'):
    self.__version = str(version)
    self.__service_url = service_url
    self.__service_name = service_name

  def __getattr__(self, name):
    if self.__service_name != None:
      name = "%s.%s" % (self.__service_name, name)
    return ServiceProxy(self.__service_url, name, self.__version)
  
  def __call__(self, *args, **kwargs):
    r = urllib.urlopen(self.__service_url,
                                dumps({
                                  "jsonrpc": self.__version,
                                  "method": self.__service_name,
                                  'params': (args if args else kwargs),
                                  'id': str(uuid.uuid1())})).read()
    print r
    return loads(r)