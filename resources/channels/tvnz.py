import re, sys, time, urllib

from xml.dom import minidom

import resources.tools as tools
import resources.config as config
settings = config.__settings__
from resources.tools import webpage, Proxy
import pyamf
from pyamf import remoting
from pyamf.remoting.client import RemotingService

class tvnz:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "TVNZ"
  self.urls = dict()
  self.urls['base'] = 'http://tvnz.co.nz'
  self.urls['content'] = 'content'
  self.urls['page'] = 'ps3_xml_skin.xml'
  self.urls['search'] = 'search'
  self.urls['episodes'] = '_episodes_group'
  self.urls['extras'] = '_extras_group'
  self.urls['playerKey'] = 'AQ~~,AAAA4FQHurk~,l-y-mylVvQnoF42ofHcZUqUd1pmQEn6C'
  self.urls['publisherID'] = 963482467001
  
# http://tvnz.co.nz/video
  self.urls['const'] = 'f86d6617a68b38ee0f400e1f4dc603d6e3b4e4ed'
  self.urls['experienceID'] = 1029272630001
  self.urls['playerID'] = str(self.urls['experienceID'])
  
  self.urls['swfUrl'] = 'http://admin.brightcove.com/viewer/us20120920.1336/federatedVideoUI/BrightcovePlayer.swf'

  self.bitrate_min = 400000
  self.xbmcitems = tools.xbmcItems(self.channel)

 def url(self, folder):
  u = self.urls
  return "/".join((u['base'], u['content'], folder, u['page']))

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
  page = webpage(self.url("ps3_navigation")) # http://tvnz.co.nz/content/ps3_navigation/ps3_xml_skin.xml
  xml = self._xml(page.doc)
  if xml:
   for stat in xml.getElementsByTagName('MenuItem'):
    type = stat.attributes["type"].value
    if type in ('shows', 'alphabetical'): #, 'distributor'
     m = re.search('/([0-9]+)/',stat.attributes["href"].value)
     if m:
      item = tools.xbmcItem(self.channel)
      info = item['videoInfo']
      info["Title"] = stat.attributes["title"].value
      info["FileName"] = "%s?ch=%s&type=%s&id=%s" % (self.base, self.channel, type, m.group(1))
      self.xbmcitems.items.append(item)
   item = tools.xbmcItem(self.channel) # Search
   info = item['videoInfo']
   info["Title"] = "Search"
   info["FileName"] = "%s?ch=TVNZ&type=%s" % (self.base, "search")
   self.xbmcitems.items.append(item)
  else:
   sys.stderr.write("No XML Data")
  return self.xbmcitems.addall()

 def show(self, id, search = False):
  if search:
   import urllib
   url = "%s/%s/%s?q=%s" % (self.urls['base'], self.urls['search'], self.urls['page'], urllib.quote_plus(id))
  else:
   url = self.url(id)
  page = webpage(url)
  xml = self._xml(page.doc)
  if xml:
   for show in xml.getElementsByTagName('Show'):
    se = re.search('/content/(.*)_(episodes|extras)_group/ps3_xml_skin.xml', show.attributes["href"].value)
    if se:
     if se.group(2) == "episodes":
      #videos = int(show.attributes["videos"].value) # Number of Extras
	  #episodes = int(show.attributes["episodes"].value) # Number of Episodes
      #channel = show.attributes["channel"].value
      item = tools.xbmcItem(self.channel)
      info = item['videoInfo']
      info["FileName"] = "%s?ch=%s&type=singleshow&id=%s%s" % (self.base, self.channel, se.group(1), self.urls['episodes'])
      info["Title"] = show.attributes["title"].value
      info["TVShowTitle"] = info["Title"]
      #epinfo = self.firstepisode(se.group(1))
      #if epinfo:
      # info = dict(epinfo.items() + info.items())
      self.xbmcitems.items.append(item)
  #self.xbmcitems.type = "tvshows"
  return self.xbmcitems.addall()

 def search(self):
  results = self.xbmcitems.search()
  if results:
   self.show(results, True)

 def episodes(self, id):
  page = webpage(self.url(id))
  if page.doc:
   xml = self._xml(page.doc)
   if xml:
    #for ep in xml.getElementsByTagName('Episode').extend(xml.getElementsByTagName('Extra')):
    #for ep in map(xml.getElementsByTagName, ['Episode', 'Extra']):
    count = xml.getElementsByTagName('Episode').length
    for ep in xml.getElementsByTagName('Episode'):
     item = self._episode(ep)
     if item:
      self.xbmcitems.items.append(item)
    for ep in xml.getElementsByTagName('Extras'):
     item = self._episode(ep)
     if item:
      self.xbmcitems.items.append(item)
    #self.xbmcitems.sorting.append("DATE")
    #self.xbmcitems.type = "episodes"
    #self.xbmcitems.addall()
    return self.xbmcitems.addall()


 def firstepisode(self, id):
  page = webpage(self.url(id + self.urls['episodes']))
  if page.doc:
   xml = self._xml(page.doc)
   if xml:
    item = self._episode(xml.getElementsByTagName('Episode')[0])
    if item:
     return item['videoInfo']
  return False

 def _episode(self, ep):
  #se = re.search('/([0-9]+)/', ep.attributes["href"].value)
  se = re.search('([0-9]+)', ep.attributes["href"].value)
  if se:
   item = tools.xbmcItem(self.channel)
   link = se.group(1)
   if ep.firstChild:
    item['videoInfo']["Plot"] = ep.firstChild.data.strip()
   title = ep.attributes["title"].value
   subtitle = ep.attributes["sub-title"].value
   if not subtitle:
    titleparts = title.split(': ', 1) # Some Extras have the Title and Subtitle put into the title attribute separated by ': '
    if len(titleparts) == 2:
     title = titleparts[0]
     subtitle = titleparts[1]
   sxe = ""
   episodeparts = ep.attributes["episode"].value.split('|')
   if len(episodeparts) == 3:
    #see = re.search('Series ([0-9]+), Episode ([0-9]+)', episodeparts[0].strip()) # Need to catch "Episodes 7-8" as well as "Epsiode 7". Also need to catch episode without series
    see = re.search('(?P<s>Se(ries|ason) ([0-9]+), )?Episodes? (?P<e>[0-9]+)(-(?P<e2>[0-9]+))?', episodeparts[0].strip())
    if see:
     try:
      item['videoInfo']["Season"]  = int(see.group("s"))
     except:
      item['videoInfo']["Season"] = 1
     item['videoInfo']["Episode"] = int(see.group("e"))
    sxe = item.sxe()
    if not sxe:
      sxe = episodeparts[0].strip() # E.g. "Coming Up" or "Catch Up"
    date = self._date(episodeparts[1].strip())
    if date:
     item['videoInfo']["Date"] = date
    item['videoInfo']["Premiered"] = episodeparts[1].strip()
    item['videoInfo']["Duration"] = self._duration(episodeparts[2].strip())
   item['videoInfo']["TVShowTitle"] = title
   item['videoInfo']["Title"] = " ".join((title, sxe, subtitle)) #subtitle
   item['videoInfo']["Thumb"] = ep.attributes["src"].value
   item['playable'] = True
   item['videoInfo']["FileName"] = "%s?ch=%s&id=%s&info=%s" % (self.base, self.channel, link, item.infoencode())
   return item
  else:
   sys.stderr.write("_episode: No se")

 def play(self, id, encodedinfo):
  item = tools.xbmcItem(self.channel)
  item.infodecode(encodedinfo)
  item['fanart'] = self.xbmcitems.fanart
  item['urls'] = self._geturls(id, item['videoInfo']["Thumb"])
  item['playable'] = True
  item['videoInfo']['id'] = id
  return self.xbmcitems.resolve(item, self.channel)

 def _geturls(self, id, thumb):
  qsdata = { 'width': 640, 'height': 410, 'flashID' : 'myExperience%s' % id,
             'bgcolor': '#171e2a', 'wmode': 'opaque', 'isVid': True,
             'playerID': self.urls['playerID'], 'isUI': True,
             'publisherID': self.urls['publisherID'], 'dynamicStreaming': False,
             'autoStart': False, '@videoPlayer': 'ref:%s' % id,
             'debuggerID': '' }
  self.swfUrl = self.GetSwfUrl(qsdata)
  urls = dict()
  urlinfo = re.search('http://images.tvnz.co.nz/tvnz_(?:site_)?images/(.*?)/[0-9]+/[0-9]+/(.*?)(?:_E3)?.jpg', thumb)
  if urlinfo:
   url = '%s/%s/%s' % (self.urls['base'], urlinfo.group(1).replace("_", "-"), urlinfo.group(2)[len(urlinfo.group(1)) + 1:].replace("_", "-") + "-video-" + id)
   rtmpdata = self.get_clip_info(int(id), url)
   if rtmpdata:
    for rendition in rtmpdata:
     urls[rendition["encodingRate"]] = rendition["defaultURL"] + ' swfUrl=' + self.swfUrl
  return urls

 def _printResponse(self, response):
  import pprint
  pp = pprint.PrettyPrinter()
  print "pprint response:"
  pp.pprint(response)
  print "pprint programmedContent:"
  pp.pprint(response['programmedContent'])
  print "pprint videoPlayer:"
  pp.pprint(response['programmedContent']['videoPlayer'])
  print "pprint mediaDTO:"
  pp.pprint(response['programmedContent']['videoPlayer']['mediaDTO'])
  print "pprint renditions:"
  pp.pprint(response['programmedContent']['videoPlayer']['mediaDTO']['renditions'])

 def get_clip_info(self, contentID, url):
  serviceUrl = "http://c.brightcove.com/services/messagebroker/amf?playerId=" + self.urls['playerID']
  serviceName = "com.brightcove.experience.ExperienceRuntimeFacade"
  proxy = Proxy()
  client = RemotingService(serviceUrl, amf_version=3,
                           user_agent=webpage().fullagent('chrome'))
  client.setProxy(proxy.httpProxyString, type='http')
  service = client.getService(serviceName)

  pyamf.register_class(ViewerExperienceRequest,
                       'com.brightcove.experience.ViewerExperienceRequest')
  pyamf.register_class(ContentOverride,
                       'com.brightcove.experience.ContentOverride')

  content_override = ContentOverride(contentId=float("nan"),
                                     contentRefId=str(contentID))
  viewer_exp_req = ViewerExperienceRequest(url, [content_override],
                                           int(self.urls['playerID']), "")

  response = service.getDataForExperience(self.urls['const'], viewer_exp_req)

  #self._printResponse(response)
  return response['programmedContent']['videoPlayer']['mediaDTO']['renditions']

 def advert(self, chapter):
  advert = chapter.getElementsByTagName('ref')
  if len(advert):
   # fetch the link - it'll return a .asf file
   page = webpage(advert[0].attributes['src'].value)
   if page.doc:
    xml = self._xml(page.doc)
    if xml:
     # grab out the URL to the actual flash ad
     for flv in xml.getElementsByTagName('FLV'):
      if flv.firstChild and len(flv.firstChild.wholeText):
       return(flv.firstChild.wholeText)

 def _duration(self, dur):
  # Durations are formatted like 0:43:15
  duration = 0
  parts = dur.split(":")
  for part in parts:
   duration *= 60
   duration += int(part)
  return duration

 def _date(self, str):
#  import datetime
#  # Dates are formatted like 23 Jan 2010.
#  # Can't use datetime.strptime as that wasn't introduced until Python 2.6
#  formats = ["%d %b %y", "%d %B %y", "%d %b %Y", "%d %B %Y"]
#  for format in formats:
#   try:
#    return datetime.datetime.strptime(str, format).strftime("%d.%m.%Y")
#   except:
#    pass
#  return False
  return str

 def GetSwfUrl(self, qsData):
  url = "http://c.brightcove.com/services/viewer/federated_f9?&" + urllib.urlencode(qsData)
  page = webpage(url, agent='chrome')
  location = page.redirUrl
  base = location.split(u"?",1)[0]
  location = base.replace(u"BrightcoveBootloader.swf", u"federatedVideoUI/BrightcoveBootloader.swf")
  return location


class ContentOverride(object):
 def __init__(self, contentId = 0, contentRefId = None, contentType = 0, target = 'videoPlayer'):
  self.contentType = contentType
  self.contentId = contentId
  self.target = target
  self.contentIds = None
  self.contentRefId = contentRefId
  self.contentRefIds = None
  self.featuredId = float("nan")
  self.featuredRefId = None

class ViewerExperienceRequest(object):
 def __init__(self, URL, contentOverrides, experienceId, playerKey, TTLToken = ''):
  self.TTLToken = TTLToken
  self.URL = URL
  self.deliveryType = float("nan")
  self.contentOverrides = contentOverrides
  #self.contentOverrides = []
  self.experienceId = experienceId
  self.playerKey = playerKey
