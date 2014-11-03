import urllib, re, sys
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulStoneSoup

import resources.tools as tools
import resources.config as config
settings = config.__settings__
from resources.tools import webpage
from xml.dom import minidom

class ziln:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "Ziln"
  self.urls = dict()
  self.urls['base'] = 'http://www.ziln.co.nz'
  self.urls["rtmp1"] = 'rtmp://flash1.e-cast.co.nz'
  self.urls["rtmp2"] = 'ecast'
  self.urls["rtmp3"] = 'mp4:/ziln'
  self.xbmcitems = tools.xbmcItems(self.channel)

 def index(self):
  item = tools.xbmcItem(self.channel)
  info = item['videoInfo']
  info["Title"] = "Channels"
  info["FileName"] = "%s?ch=Ziln&folder=channels" % sys.argv[0]
  self.xbmcitems.items.append(item)
  item = tools.xbmcItem(self.channel)
  info = item['videoInfo']
  info["Title"] = "Search"
  info["Thumb"] = "DefaultVideoPlaylists.png"
  info["FileName"] = "%s?ch=Ziln&folder=search" % sys.argv[0]
  self.xbmcitems.items.append(item)
  return self.xbmcitems.addall()

 def programmes(self, type, urlext):
  if type == "channel":
   folder = 1
   url = self.urls['base']
  elif type == "video":
   folder = 0
   url = "%s/assets/php/slider.php?channel=%s" % (self.urls['base'], urlext)
  elif type == "search":
   folder = 0
   url = "%s/search?search_keyword=%s" % (self.urls['base'], urlext.replace(" ", "+"))
  page = webpage(url)
  if page.doc:
   if type == "channel" or type == "search":
    div_tag = SoupStrainer('div')
    html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
    programmes = html_divtag.findAll(attrs={'class' : 'programmes'})
   elif type == "video":
    div_tag = SoupStrainer('body')
    html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
    programmes = html_divtag.findAll(attrs={'class' : 'slider slider-small'})
   if type == "search":
    type = "video"
   if len(programmes) > 0:
    for program in programmes:
     list = program.find('ul')
     if list:
      listitems = list.findAll('li')
      count = len(listitems)
      if count > 0:
       for listitem in listitems:
        link = listitem.find('a', attrs={'href' : re.compile("^/%s/" % type)})
        if link.img:
         if re.search("assets/images/%ss/" % type, link.img["src"]):
          item = tools.xbmcItem(self.channel)
          if listitem.p.string:
           item['videoInfo']["Title"] = listitem.p.string.strip()
          else:
           item['videoInfo']["Title"] = link.img["alt"]
          item['videoInfo']["Thumb"] = "%s/%s" % (self.urls['base'], link.img["src"])
          index = re.search("assets/images/%ss/([0-9]*?)-mini.jpg" % type, link.img["src"]).group(1)
          item['videoInfo']["FileName"] = "%s?ch=%s&%s=%s" % (self.base, self.channel, type, urllib.quote(index))
          if type == "video":
           item['playable'] = True
          self.xbmcitems.items.append(item)
       else:
        return self.xbmcitems.addall()
     else:
      sys.stderr.write("Search returned no results")
   else:
    sys.stderr.write("Couldn't find any programs")
  else:
   sys.stderr.write("Couldn't get page")

 def search(self):
  results = self.xbmcitems.search()
  if results:
   return self.programmes("search", results)

 def play(self, index):
  item = tools.xbmcItem(self.channel)
  item['playable'] = True
  item['videoInfo'].update(self._getMetadata(index))
  item['urls'] = item['videoInfo'].pop('urls')
  return self.xbmcitems.resolve(item, self.channel)

 def _getMetadata(self, index):
  metadata = {}
  page = webpage("%s/playlist/null/%s" % (self.urls['base'], index))
  if page.doc:
   metadata['id'] = index
   xmldom = self._xml(page.doc)
   if not xmldom:
    return {}
   metadata['Title'] = xmldom.getElementsByTagName('title')[0].firstChild.data.strip()
   metadata['Plot'] = xmldom.getElementsByTagName('description')[0].firstChild.data.strip()
   metadata['Thumb'] = xmldom.getElementsByTagName('jwplayer:image')[0].firstChild.nodeValue
   if not metadata['Thumb'].startswith("http://"):
    metadata['Thumb'] = self.urls['base'] + metadata['Thumb']
   srcUrls = xmldom.getElementsByTagName('jwplayer:source')
   urls = {}
   for srcUrl in srcUrls:
    url = srcUrl.getAttribute('file')
    if not url.startswith("http://"):
     url = self.urls['base'] + url
    # in format 720p or 540p
    size = srcUrl.getAttribute('label')
    size = int(size[:-1])
    urls[size] = url
   metadata['urls'] = urls
   return metadata

 def _xml(self, doc):
  try:
   document = minidom.parseString(doc)
  except Exception as e:
   print e
   pass
  else:
   if document:
    return document.documentElement
  sys.stderr.write("No XML Data")
  return False

