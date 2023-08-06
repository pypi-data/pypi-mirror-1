import _vnstaty
from time import sleep

class Interface(object):
    def __init__(self, interface_name):
        """
        """
        self.name = interface_name
        try:
            _vnstaty.getifinfo(self.name)
        except:
            raise Exception('Unable to use %s' % self.name)
        
    def info(self):  
        return _vnstaty.getifinfo(self.name)

    def get_usage(self, delta=60):
        """Get the bandwidth usage in the given delta (seconds)
        
        >>> interface = Interface('eth0')
        >>> dict = interface.get_usage(1)
        >>> dict == {'bytes_in': 0, \
            'bytes_out': 0,\
            'packages_in': 0,\
            'packages_out': 0}
        True
        """

        start_info = self.info()
        sleep(delta)
        end_info = self.info()

        info = {}
        
        info['bytes_in'] = end_info['bytes_in'] - start_info['bytes_in']
        info['bytes_out'] = end_info['bytes_out'] - start_info['bytes_out']
        info['packages_in'] = end_info['packages_in'] - \
                              start_info['packages_in']
        info['packages_out'] = end_info['packages_out'] - \
                               start_info['packages_out']
        
        return info 
