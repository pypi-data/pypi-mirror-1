'''The Kitchen Sink

$License$

$Id: __init__.py 159 2005-12-02 20:35:19Z drew $
'''

__all__ = ['aspout', 'source', 'console', 'config', 'rules']

#import xix.utils.string
import xix.utils.config
#import xix.utils.rules # we can't load this here due to config setup dependency

__author__    = 'Drew Smathers <drew.smathers@gmail.com>'
__version__   = '$Revision: 159 $'[11:-2]
__copyright__ = 'Copyright (C) 2005, Drew Smathers'
__license__   = 'MIT'

