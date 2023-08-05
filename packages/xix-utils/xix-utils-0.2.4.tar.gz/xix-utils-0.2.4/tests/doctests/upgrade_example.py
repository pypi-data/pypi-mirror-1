from xix.utils.upgrade import upgrade

def upgrade0_0_0():
    print 'upgrading from 0.0.0'

def upgrade0_0_1():
    print 'upgrading from 0.0.1'

def upgrade1_0_2():
    print 'upgrading from 1.0.2'

def upgrade1023_2():
    print 'upgrading from 1023.2'

def downgrade0_0_0():
    print 'downgrading to 0.0.0'

def downgrade0_0_1():
    print 'downgrading to 0.0.1'

def downgrade1_0_2():
    print 'downgrading to 1.0.2'

def downgrade1023_2():
    print 'downgrading to 1023.2'

def foo0_0_0():
    print 'foo 0.0.0'

def foo0_0_1():
    print 'foo 0.0.1'

def foo1_0_2():
    print 'foo 1.0.2'

def foo1023_2():
    print 'foo 1023.2'

def do_upgrade(vers):
    upgrade(vers, globals())

