import os

# interface, time_period (seconds)
INTERFACES = ( 
#    ('lo', 300),
    ('en1', 60),
)

HOME = os.environ['HOME'] 

CONNECTION_STRING = 'sqlite:///' + HOME + '/vnstaty.db'
