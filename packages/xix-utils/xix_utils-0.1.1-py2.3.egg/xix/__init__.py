# Internal configuration setup
from xix.utils.config import configFactory
import os
from pkg_resources import resource_filename

pj = os.path.join
dir = os.path.dirname

#configFactory.addResource('app.cfg', pj(dir(__file__), '__app__.cfg'))
configFactory.addResource('app.cfg', resource_filename(__name__, '__app__.cfg'))

_cfg = configFactory.getConfig('app.cfg')

configFactory.addResource('xix.utils.rules', config=_cfg.xix.utils.rules)

