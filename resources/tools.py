# Generic functions

import sys, re, os
import resources.config as config
import logging
logging.basicConfig(level=logging.DEBUG)
settings = config.__settings__
# import xbmc # http://xbmc.sourceforge.net/python-docs/xbmc.html
#import xbmcgui # http://xbmc.sourceforge.net/python-docs/xbmcgui.html
#import xbmcplugin # http://xbmc.sourceforge.net/python-docs/xbmcplugin.html

#def initaddon:
# import shutil, os
# shutil.rmtree(__cache__)
# os.mkdir(__cache__)

logger = logging.getLogger(__name__)

class webpage:
 def __init__(self, url = "", agent = 'ps3', cookie = "", type = ""):
  self.doc = ""
  self.agent = agent
  self.cookie = cookie
  self.type = type
  self.proxy = "103.16.180.117"
  self.proxy_port = 443
  self.socks_port = 465
  if url:
   self.url = url
   self.get(url)

 def get(self, url):
  import urllib2
  proxy_handler = urllib2.ProxyHandler({'http':'%s:%s'%(self.proxy,self.proxy_port)})
  opener = urllib2.build_opener(proxy_handler)
  urllib2.install_opener(opener)
  print "Requesting URL: %s" % (url)
  req = urllib2.Request(url)
  req.add_header('User-agent', self.fullagent(self.agent))
  if self.cookie:
   req.add_header('Cookie', self.cookie)
  if self.type:
   req.add_header('content-type', self.type)
  try:
   response = urllib2.urlopen(req, timeout = 20)
   self.doc = response.read()
   response.close()
  except urllib2.HTTPError, err:
   sys.stderr.write("urllib2.HTTPError requesting URL: %s" % (err.code))
  else:
   return self.doc

 def xml(self):
  from xml.dom import minidom
  #from xml.parsers.expat import ExpatError
  try:
   document = minidom.parseString(self.doc)
   if document:
    self.xmldoc = document.documentElement
    return self.xmldoc
  except: # ExpatError: # Thrown if the content contains just the <xml> tag and no actual content. Some of the TVNZ .xml files are like this :(
   return False

 def html(self):
  from BeautifulSoup import BeautifulSoup
  try:
   return BeautifulSoup(self.doc)
  except:
   pass

 def fullagent(self, agent):
  if agent == "ps3":
   return 'Mozilla/5.0 (PLAYSTATION 3; 3.55)'
  elif agent == 'iphone':
   return 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1C25 Safari/419.3'
  elif agent == 'ipad':
   return 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
  else: # Chrome
   return 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204 Safari/534.16'



class xbmcItem(dict):
 def __init__(self, channel=None):
  self['path'] = ""
  self['videoInfo'] = { 'Icon' : 'DefaultVideo.png', 'Thumb' : '' }
  self['playable'] = False
  self['urls'] = dict()
  self['units'] = "kbps"
  if channel:
   self['channel'] = channel
  else:
   self['channel'] = ""
  self['fanart'] = ""

 def applyURL(self, bitrate):
  if bitrate in self['urls']:
   self['videoInfo']["FileName"] = self['urls'][bitrate]

 def stack(self, urls): #Build a URL stack from multiple URLs for the XBMC player
  if len(urls) == 1:
   return urls[0]
  elif len(urls) > 1:
   return "stack://" + " , ".join([url.replace(',', ',,').strip() for url in urls])
  return False

 def sxe(self):
  if 'Season' in self['videoInfo'] and 'Episode' in self['videoInfo']:
   return str(self['videoInfo']["Season"]) + "x" + \
          str(self['videoInfo']["Episode"]).zfill(2)
  return False

 def unescape(self, s): #Convert escaped HTML characters back to native unicode, e.g. &gt; to > and &quot; to "
  from htmlentitydefs import name2codepoint
  return re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

 def titleplot(self): #Build a nice title from the program title and sub-title (given as PlotOutline)
  if self['videoInfo']['PlotOutline']:
   self['videoInfo']['Title'] = "%s - %s" % (self['videoInfo']['TVShowTitle'],
                                             self['videoInfo']['PlotOutline'])

 def url(self, urls = False, quality = 'High'): # Low, Medium, High
  if not urls:
   urls = self['urls']
  if quality == 'Medium' and len(self['urls']) > 2:
   del urls[max(urls.keys())]
  if quality == 'Low':
   return self.stack(urls[min(urls.keys())])
  else:
   return self.stack(urls[max(urls.keys())])

 def encode(self):
  return self._encode(self)

 def infoencode(self):
  return self._encode(self['videoInfo'])

 def _encode(self, toencode):
  import json, urllib
  return urllib.quote(json.dumps(toencode))

 def decode(self, item):
  return self.bitrates(self._decode(item))

 def infodecode(self, info):
  self['videoInfo'] = self._decode(info)

 def _decode(self, todecode):
  import json, urllib
  return json.loads(urllib.unquote(todecode))


class xbmcItems:
 def __init__(self, channel = ""):
  self.items = list()
  self.fanart = "fanart.jpg"
  self.channel = ""
  if channel:
   self.channel = channel
   self.fanart = os.path.join('extrafanart', channel + '.jpg')
  self.sorting = ["UNSORTED", "LABEL"] # ALBUM, ALBUM_IGNORE_THE, ARTIST, ARTIST_IGNORE_THE, DATE, DRIVE_TYPE, DURATION, EPISODE, FILE, GENRE, LABEL, LABEL_IGNORE_THE, MPAA_RATING, NONE, PLAYLIST_ORDER, PRODUCTIONCODE, PROGRAM_COUNT, SIZE, SONG_RATING, STUDIO, STUDIO_IGNORE_THE, TITLE, TITLE_IGNORE_THE, TRACKNUM, UNSORTED, VIDEO_RATING, VIDEO_RUNTIME, VIDEO_TITLE, VIDEO_YEAR
  self.type = ""

 def _listitem(self, item):
  if 'videoInfo' in item:
   info = item['videoInfo']
   listitem = { 'label' : info["Title"], 'icon' : info["Icon"],
                'thumbnail' : info["Thumb"]}
   if 'fanart' in item:
    listitem['fanart'] = os.path.join(config.__path__, item['fanart'])
   else:
    listitem['fanart'] = os.path.join(config.__path__, self.fanart)
   listitem.update({'type' : "video", 'videoInfo' : info})
   return listitem
  else:
   sys.stderr.write("No Item Info")
   return {}

 def _add(self, item, total = 0): #Add a list item (media file or folder) to the XBMC page
  # http://xbmc.sourceforge.net/python-docs/xbmcgui.html#ListItem
  listitem = self._listitem(item)
  if listitem:
   if 'channel' in item and item['channel']:
    channel = item['channel']
   else:
    channel = self.channel
   listitem['channel'] = channel
   itemFolder = True
   if 'playable' in item:
    if settings.get(channel, 'quality_choose') != 'True':
      itemFolder = False
   info = item.get('videoInfo', {})
   if 'FileName' in info:
    if not sys.argv[0] in info['FileName']:
     itemFolder = False
   else:
    if len(item['urls']) > 0:
     if len(item['urls']) == 1:
      itemFolder = False
      info['FileName'] = item['urls'].itervalues().next()
     else:
      if settings.get(channel, 'quality_choose') == 'False':
       itemFolder = False
       info['FileName'] = self.quality(item['urls'], self.channel)
      else:
       info['FileName'] = '%s?item=%s' % (sys.argv[0], item.encode()) #TODO
   if not itemFolder:
    listitem['mimetype'] = 'video/x-msvideo'
    listitem['IsPlayable'] = True
   return listitem

 def addindex(self, index, total = 0):
  return self._add(self, self.items[index], total)

 def add(self, total):
  return self._add(self.items[-1], total)

 def addall(self):
  total = len(self.items)
  return [ self._add(item, total) for item in self.items ]

 def resolve(self, item, channel):
  if settings.get(channel, 'quality_choose') == 'True':
   self.bitrates(item)
  else:
   if 'FileName' in item['videoInfo']:
    return self.play(item, item['videoInfo']['FileName'])
   else:
    return self.play(item, self.quality(item['urls'], channel))

 def play(self, item, url):
  urlType = "unknown"
  if not url:
   urlType = "none"
  elif url.startswith("http://"):
   urlType = "http"
  listitem = { 'path' : url, 'type' : urlType, 'IsPlayable' : True }
  item.update(listitem)
  if 'urls' in item:
   del item['urls']
  if 'units' in item:
   del item['units']
  return item

 def bitrates(self, sourceitem):
  total = len(sourceitem['urls'])
  for bitrate, url in sourceitem['urls'].iteritems():
   item = {}
   try:
    item['fanart'] = sourceitem['fanart']
   except:
    pass
   item['videoInfo'] = dict(sourceitem['videoInfo'])
   item['videoInfo']['Title'] += " (" + str(bitrate) + " " + sourceitem['units'] + ")"
   item['videoInfo']['FileName'] = url
   #item.urls[bitrate] = (self.stack(url))
   self.items.append(item)
  return self.addall()

#  def itemtobitrates(self, item):
#   itemtoitems(decode(item))

# def sort(self):
#  import xbmcplugin
#  for method in self.sorting:
#   xbmcplugin.addSortMethod(handle = config.__id__, sortMethod = getattr(xbmcplugin, "SORT_METHOD_" + method))
#   #xbmcplugin.addSortMethod(handle = config.__id__, sortMethod = xbmcplugin.SORT_METHOD_UNSORTED)
#  if self.type:
#   xbmcplugin.setContent(handle = config.__id__, content = self.type)
#  xbmcplugin.endOfDirectory(config.__id__)

 def search(self):
  # want to return the parsed arg
  # TODO
  return False

 def quality(self, urls, channel): # Low, Medium, High
  if len(urls) == 0:
   return False
  quality = settings.get(channel, 'quality')
  if quality in ['High', 'Medium', 'Low']:
   if len(urls) > 0:
    if quality == 'Medium' and len(urls) > 2:
     del urls[max(urls.keys())]
    if quality == 'Low':
     return self.stack(urls[min(urls.keys())])
    else:
     return self.stack(urls[max(urls.keys())])
  return self.stack(urls[max(urls.keys())])

 def decode(self, item):
  return self.bitrates(self._decode(item))

 def _decode(self, todecode):
  import json, urllib
  return json.loads(urllib.unquote(todecode))

 def stack(self, urls): #Build a URL stack from multiple URLs for the XBMC player
  if type(urls) is str or type(urls) is unicode:
   return urls
  if len(urls) == 1:
   return urls[0]
  elif len(urls) > 1:
   return "stack://" + " , ".join([url.replace(',', ',,').strip() for url in urls])
  return False

 def booleansetting(self, section, setting):  
  if settings.get(section, setting) == 'True':
   return True
  return False

 def message(self, message, title = "Warning"): #Show an on-screen message (useful for debugging)
#  import xbmcgui
#  dialog = xbmcgui.Dialog()
#  if message:
#   if message != "":
#    dialog.ok(title, message)
#   else:
#    dialog.ok("Message", "Empty message text")
#  else:
#   dialog.ok("Message", "No message text")
  logger.warning(message)

 def log(self, message):
  sys.stderr.write(message)




def xbmcdate(inputdate, separator = "/"): #Convert a date in "%d/%m/%y" format to an XBMC friendly format
 return inputdate
 #import time, xbmc
 #return time.strftime(xbmc.getRegion("datelong").replace("DDDD,", "").replace("MMMM", "%B").replace("D", "%d").replace("YYYY", "%Y").strip(), time.strptime(inputdate, "%d" + separator + "%m" + separator + "%y"))



