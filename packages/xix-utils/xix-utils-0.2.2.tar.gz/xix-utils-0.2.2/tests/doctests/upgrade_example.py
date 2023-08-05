from xix.utils.upgrade import upgrade

def upgrade0_0_0():
    print 'upgrading from 0.0.0'

def upgrade0_0_1():
    print 'upgrading from 0.0.1'

def upgrade1_0_2():
    print 'upgrading from 1.0.2'

def upgrade1023_2():
    print 'upgrading from 1023.2'

def do_upgrade(vers):
    upgrade(vers, globals())

