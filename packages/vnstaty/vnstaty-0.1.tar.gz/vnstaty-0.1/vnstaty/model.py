import datetime as datetime
from sqlalchemy import and_
from elixir import Entity, Field, Integer, String, DateTime
from elixir import metadata, setup_all, create_all, session

class IfStats(Entity):
    id = Field(Integer, primary_key=True, autoincrement=True)
    interface = Field(String)
    bytes_in = Field(Integer)
    bytes_out = Field(Integer)
    packages_in = Field(Integer)
    packages_out = Field(Integer)
    timestamp = Field(DateTime)
    
    def __init__(self, interface):
        self.iface = interface
        self.interface = interface.name
        self.timestamp = datetime.datetime.now()

        info = interface.info()
        self.bytes_in = info['bytes_in']
        self.bytes_out = info['bytes_out']
        self.packages_in = info['packages_in']
        self.packages_out = info['packages_out']
    
    # Static method to get the tuples in a given period of time
    def get_period(interface, start_date, end_date):
        result = IfStats.query.filter(
            and_(
                IfStats.interface == interface,
                IfStats.timestamp >= start_date,
                IfStats.timestamp <= end_date,
            )
        )
        return result
    get_period = staticmethod(get_period)

    def __repr__(self):
        return "<IfStats('%s','%s')>" % (self.interface, self.timestamp)


metadata.bind = 'sqlite:///vnstaty.db'
metadata.bind.echo = True
setup_all()
create_all()

del Entity, Field, Integer, String, DateTime, metadata, setup_all, create_all
