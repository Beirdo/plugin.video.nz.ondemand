import urllib, re, sys
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulStoneSoup

import resources.tools as tools
import resources.config as config
settings = config.__settings__
from resources.tools import webpage
from xml.dom import minidom

class stuff:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "Stuff"
  self.urls = dict()
  self.urls['base'] = 'http://www.stuff.co.nz'
  self.urls['videos'] = 'videos'
  self.xbmcitems = tools.xbmcItems(self.channel)
  self.prefetch = self.xbmcitems.booleansetting(self.channel, 'prefetch')

 def _xml(self, doc):
  try:
   document = minidom.parseString(doc)
  except:
   pass
  else:
   if document:
    return document.documentElement
  sys.stderr.write("No XML Data")
  return False


 def index(self):
  page = webpage(self.urls['base'])
  if page.doc:
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   menu = html_divtag.find(attrs = {'id' : 'home_nav'})
   if menu:
    menuitems = menu.findAll('a')
    for menuitem in menuitems:
     item = tools.xbmcItem(self.channel)
     item['videoInfo']["Title"] = menuitem.string
     item['videoInfo']["FileName"] = "%s?ch=%s&section=%s" % (self.base, self.channel, menuitem["href"][1:-1])
     self.xbmcitems.items.append(item)
    return self.xbmcitems.addall()
   else:
    sys.stderr.write("index: no menu")
  else:
   sys.stderr.write("index: no page.doc")

 def sections(self, section):
  page = webpage('%s/%s/%s/' % (self.urls['base'], section, self.urls['videos']))
  if page.doc:
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   #landing = html_divtag.find(attrs = {'id' : 'landing_video'})
   gallery = html_divtag.find(attrs = {'class' : 'gallery_box'})
   if gallery:
    videos = gallery.findAll('div')
    if len(videos) > 0:
     for video in videos:
      link = video.find("a")
      if link:
       if link.string:
        item = tools.xbmcItem(self.channel)
        link = video.find("a")
        item['videoInfo']["Title"] = link.string.strip()
        image = video.find("img")
        if image:
         item['videoInfo']["Thumb"] = image['src']
        videoid = re.match('/%s/%s/([0-9]+)/' % (section, self.urls['videos']), link['href'])
        if videoid:
         if self.prefetch:
          item.urls = [self._geturl(section, videoid)]
         else:
          item.playable = True
          item['videoInfo']["FileName"] = "%s?ch=%s&section=%s&id=%s" % (self.base, self.channel, section, videoid.group(1))
         self.xbmcitems.items.append(item)
     return self.xbmcitems.addall()
    else:
     sys.stderr.write("sections: no videos")
   else:
    sys.stderr.write("sections: no gallery_box")
  else:
   sys.stderr.write("sections: no page.doc")

 def play(self, section, id):
  item = tools.xbmcItem(self.channel)
  item['id'] = id
  item['playable'] = True
  item['videoInfo'].update(self._getMetadata(section, id))
  url = item['videoInfo'].pop('url')

  return self.xbmcitems.play(item, url)

 def _geturl(self, section, id):
  page = webpage("/".join((self.urls['base'], section, self.urls['videos'], id)))
  if page.doc:
   videourl = re.search('{file: "(http://(.*?).mp4)"}', page.doc)
   if videourl:
    return videourl.group(1)

 def _getMetadata(self, section, id):
  metadata = {}
  page = webpage("/".join((self.urls['base'], section, self.urls['videos'], id)))
  if page.doc:
   soup = BeautifulSoup(page.doc)
   description = soup.find('meta', attrs={"name" : "description"})['content']

   thumbnail = soup.find('link', attrs={'rel' : 'image_src'})['href']
   videosrc = soup.find('link', attrs={'rel' : 'video_src'})['href']
   match = re.search(r'mediaXML=(.*?)(?:&amp;|$)', videosrc)
   if match:
    xmlfile = match.group(1)
   else:
    xmlfile = None

   metadata['Plot'] = description
   metadata['thumbnail'] = thumbnail

   if xmlfile:
    xmlpage = webpage(xmlfile)
    if xmlpage:
     xmldom = self._xml(xmlpage.doc)
     title = xmldom.getElementsByTagName('title')[0].firstChild.nodeValue
     url = xmldom.getElementsByTagName('media:content')[0].getAttribute('url')
     metadata['Title'] = title
     metadata['url'] = url

  return metadata

