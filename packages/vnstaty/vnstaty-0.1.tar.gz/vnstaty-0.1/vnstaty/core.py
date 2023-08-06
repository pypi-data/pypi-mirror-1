import _vnstaty

class Interface(object):
    def __init__(self, interface_name):
        self.name = interface_name
        try:
            _vnstaty.getifinfo(self.name)
        except:
            raise Exception('Unable to use %s' % self.name)
        
    def info(self):  
        return _vnstaty.getifinfo(self.name)
