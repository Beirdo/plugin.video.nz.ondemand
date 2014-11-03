import sys
import resources.tools as tools

class prime:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "Prime"
  self.urls = dict()
  self.urls['base'] = 'http://www.primetv.co.nz/Portals/1/PrimeNewsVideo/'
  self.urls['file1'] = 'PRIME_'
  self.urls['file2'] = '_Flash.flv'
  self.programs = dict()
  self.programs['News'] = "Prime News: First At 5:30 brings you the top news and sports stories from New Zealand and around the world."
  self.programs['Sport'] = "Business & Sport News"
  self.programs['Weather'] = "The Weather News"
  self.xbmcitems = tools.xbmcItems(self.channel)
  for channel, description in self.programs.iteritems():
   item = tools.xbmcItem(channel, self.channel)
   item['videoInfo']['Title'] = channel
   item['videoInfo']["Plot"] = description
   item['videoInfo']['FileName'] = self.urls['base'] + self.urls['file1'] + channel.upper() + self.urls['file2']
   item.update(self.xbmcitems.play(item, item['videoInfo']['FileName']))
   self.xbmcitems.items.append(item)

 def get(self):
  return self.xbmcitems.items
