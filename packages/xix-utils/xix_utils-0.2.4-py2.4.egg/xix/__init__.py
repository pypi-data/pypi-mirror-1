# Internal configuration setup
from xix.utils.config import configFactory
import os

pj = os.path.join
dir = os.path.dirname

#############################################################
# BEGIN xplat and dependency reduction hacks
# Adataptor for folks who are too lazy to install setuptools
try:
    from pkg_resources import resource_filename
except:
    import os, sys
    def resource_filename(name, relname):
        root = os.path.split(sys.modules[name].__file__)[0]
        fname = os.path.abspath(os.path.join(root, relname))
        return fname
# win32 adaptor for getoutput from commands module
from commands import getoutput
if os.sys.platform in ('win32', 'nt'):
    def getoutput(cmd):
        output = os.popen2(cmd)[1]
        return output.read()
# END
##############################################################
    
#configFactory.addResource('app.cfg', pj(dir(__file__), '__app__.cfg'))
configFactory.addResource('app.cfg', resource_filename(__name__, '__app__.cfg'))

_cfg = configFactory.getConfig('app.cfg')

configFactory.addResource('xix.utils.rules', config=_cfg.xix.utils.rules)


