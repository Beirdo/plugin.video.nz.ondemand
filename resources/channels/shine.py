import os, resources.tools
from datetime import date

import resources.tools as tools
import resources.config as config
settings = config.__settings__

class shine:
 def item(self):
  #self.channel = 'Shine'
  item = tools.xbmcItem()
  item['channel'] = 'Shine'
  item['fanart'] = os.path.join('extrafanart', item['channel'] + '.jpg')
  item['videoInfo']["Title"] = 'Shine TV - Live Stream'
  item['videoInfo']["Thumb"] = os.path.join(config.__path__, "resources/images/%s.png" % item['channel'])
  item['videoInfo']["Plot"] = "Shine TV is a television network of the Rhema Broadcasting Group Inc - New Zealand's largest Christian media organisation. On-air since December 2002, Shine broadcasts 24 hours nationwide on the SKY digital and Freeview Satellite platforms, with regional channels in Canterbury, Nelson and Wellington."
  item['videoInfo']["Date"] = date.today().strftime("%d.%m.%Y")
  for quality, name in {30: 'low', 250: 'med', 1200: 'high'}.iteritems():
   item['urls'][quality] = "http://wms-rbg.harmonycdn.net/shinetv-%s?MSWMExt=.asf" % name
  return item
