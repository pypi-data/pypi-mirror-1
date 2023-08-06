import datetime as datetime
from sqlalchemy import and_
from elixir import Entity, Field, Integer, String, DateTime
from elixir import metadata, setup_all, create_all, session

from vnstaty import settings

class IfStats(Entity):
    id = Field(Integer, primary_key=True, autoincrement=True)
    interface = Field(String)
    bytes_in = Field(Integer)
    bytes_out = Field(Integer)
    packages_in = Field(Integer)
    packages_out = Field(Integer)
    timestamp = Field(DateTime)
    
    def __init__(self, interface, 
                 bytes_in, bytes_out, 
                 packages_in, packages_out):

        self.timestamp = datetime.datetime.now()

        self.interface = interface
        self.bytes_in = bytes_in
        self.bytes_out = bytes_out
        self.packages_in = packages_in
        self.packages_out = packages_out
    
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


metadata.bind = settings.CONNECTION_STRING
metadata.bind.echo = False
setup_all()
create_all()

del Entity, Field, Integer, String, DateTime, metadata, setup_all, create_all
