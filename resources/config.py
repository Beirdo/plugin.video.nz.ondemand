import sys #, xbmc, xbmcaddon
from ConfigParser import SafeConfigParser

configfile = '/opt/prf/persist/newzealand/config/newzealand.conf'

config = SafeConfigParser()
config.readfp(open(configfile))

__name__ = 'plugin.video.nz.ondemand'
__settings__ = config
__cache__ = '/opt/prf/persist/newzealand/cache/%s' % __name__
__data__ = '/opt/prf/persist/newzealand/profile/%s' % __name__
__language__ = "en"
__id__ = int(sys.argv[1])
__path__ = '/opt/prf/src/plugin.video.nz.ondemand'
