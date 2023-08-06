from time import sleep
from thread import start_new_thread, allocate_lock

from vnstaty import settings
from vnstaty import Interface
from vnstaty import model

def run(interface, delta):
    while True:
        usage = interface.get_usage(delta)
        
        lock = allocate_lock()
        lock.acquire_lock()
        
        model.IfStats(
            interface.name,
            usage['bytes_in'],
            usage['bytes_out'],
            usage['packages_in'],
            usage['packages_out'],
        )
        model.session.commit()
        
        lock.release_lock()

if __name__ == "__main__":            
    for (ifname, delta) in settings.INTERFACES:
        interface = Interface(ifname)
        start_new_thread(run, (interface, delta))
    
    try:
        while True: sleep(9999) # Keep running to catch keyboard signals
    except:
        import sys
        sys.exit()
