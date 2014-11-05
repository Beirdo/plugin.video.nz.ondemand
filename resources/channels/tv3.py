# 3 News
# mms://content.mediaworks.co.nz/tv/News/TOPSTORIES.300k

import urllib, re, sys, time
from datetime import date

from BeautifulSoup import BeautifulSoup, SoupStrainer

import resources.tools as tools
import resources.config as config
settings = config.__settings__
from resources.tools import webpage

class tv3:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "TV3"
  self.channels = {"TV3": dict(), "Four": dict()}
  self.channels['TV3']['base'] = 'http://www.tv3.co.nz'
  self.channels['TV3']['ondemand'] = 'OnDemand'
  self.channels['TV3']['shows'] = 'Shows'
  self.channels['TV3']['rtmp'] = 'tv3'
  self.channels['Four']['base'] = 'http://www.four.co.nz'
  self.channels['Four']['ondemand'] = 'TV/OnDemand'
  self.channels['Four']['shows'] = 'TV/Shows'
  self.channels['Four']['rtmp'] = 'c4'
  self.urls = dict()
  self.urls['categories'] = ['Must Watch', 'Expiring Soon', 'Recently Added']
  # TitleAZ
  self.urls['base'] = 'http://www.tv3.co.nz'
  self.urls['base1'] = 'http://www'
#  self.urls['base1'] = 'http://ondemand'
  self.urls['base2'] = 'co.nz'
  self.urls['rtmp1'] = 'rtmpe://nzcontent.mediaworks.co.nz:80'
  self.urls['rtmp2'] = '_definst_/mp4:'
  self.urls['flash1'] = 'rtmpe://flashcontent.mediaworks.co.nz:80'
  self.urls['flash2'] = 'mp4:'
  self.urls['news1'] = 'rtmpe://strm.3news.co.nz'
  self.urls['http1'] = 'http://flash.mediaworks.co.nz'
  self.urls['http2'] = 'streams/_definst_//'
  self.urls['video1'] = 'tabid'
  self.urls['video2'] = 'articleID'
  self.urls['video3'] = 'MCat'
  self.urls['video4'] = 'Default.aspx'
  self.urls['feedburner_re'] = '//feedproxy\.google\.com/'
  self.urls['cat'] = '/default404.aspx?tabid='
  self.urls['cat_re'] = '/default404\.aspx\?tabid='
  self.urls['img_re'] = '\.ondemand\.tv3\.co\.nz/ondemand/AM/'
  self.urls['img_re2'] = '\.ondemand\.tv3\.co\.nz/Portals/0-Articles/'
  self.xbmcitems = tools.xbmcItems(self.channel)

 def index(self, fake = True):
  for folder in self.channels.keys():
   item = tools.xbmcItem(folder, self.channel)
   item['videoInfo']["Title"] = folder
   item['videoInfo']["FileName"] = "%s?ch=TV3&channel=%s" % (self.base, folder)
   self.xbmcitems.items.append(item)
  return self.xbmcitems.addall()

 def channelindex(self, channel): #Create second level folder for the hierarchy view, only showing items for the selected top level folder
  for category in self.urls['categories']:
   item = tools.xbmcItem(channel, self.channel)
   item['videoInfo']["Title"] = category
   item['videoInfo']["FileName"] = "%s?ch=TV3&channel=%s&cat=%s" % (self.base, channel, category.replace(" ", ""))
   self.xbmcitems.items.append(item)
  item = tools.xbmcItem(channel, self.channel)
  item['videoInfo']["Title"] = 'Shows'
  item['videoInfo']["FileName"] = "%s?ch=TV3&channel=%s&cat=%s" % (self.base, channel, "shows")
  self.xbmcitems.items.append(item)
  item = tools.xbmcItem(channel, self.channel)
  item['videoInfo']["Title"] = "Search"
  item['videoInfo']["FileName"] = "%s?ch=TV3&channel=%s&cat=%s" % (self.base, channel, "search")
  self.xbmcitems.items.append(item)
  return self.xbmcitems.addall()

 def shows(self, channel): #Create a second level list of TV Shows from a TV3 webpage
  #doc = resources.tools.gethtmlpage("%s/Shows/tabid/64/Default.aspx" % ("http://www.tv3.co.nz")) #Get our HTML page with a list of video categories
  #doc = resources.tools.gethtmlpage("%s/Shows.aspx" % ("http://www.tv3.co.nz")) #Get our HTML page with a list of video categories
  page = webpage("%s/%s/%s" % (self.channels[channel]['base'], self.channels[channel]['ondemand'], "TitleAZ.aspx"))
  if page.doc:
   html_divtag = BeautifulSoup(page.doc)
   showsdiv = html_divtag.findAll('div', attrs = {"class": "grid_2"})
   if len(showsdiv) > 0:
    for show in showsdiv:
     item = tools.xbmcItem(channel, self.channel)
     title = show.find('p').find('a')
     if title:
      if title.string:
       if title['href'][len('http://www.'):len('http://www.') + 3] == channel[0:3].lower():
        item['videoInfo']["Title"] = title.string.strip()
        image = show.find("img")
        if image:
         item['videoInfo']["Thumb"] = image['src']
        item['videoInfo']["FileName"] = "%s?ch=TV3&channel=%s&cat=%s&title=%s" % (self.base, channel, "show", urllib.quote(item['videoInfo']["Title"].replace(" ", "")))
        self.xbmcitems.items.append(item)
    return self.xbmcitems.addall()
   else:
    sys.stderr.write("showsindex: Couldn't find any videos in list")
  else:
   sys.stderr.write("showsindex: Couldn't get index webpage")


 def episodes(self, channel, cat): #Show video items from a normal TV3 webpage
  page = webpage("%s/%s/%s" % (self.channels[channel]['base'], self.channels[channel]['ondemand'], cat + ".aspx"))
  if page.doc:
   a_tag=SoupStrainer('div')
   html_atag = BeautifulSoup(page.doc, parseOnlyThese = a_tag)
   programs = html_atag.findAll(attrs={"class": re.compile(r'\bgrid_2\b')})
   if len(programs) > 0:
    for soup in programs:
     item = self._itemdiv(soup, channel)
     if item:
      self.xbmcitems.items.append(item)
      if len(item['urls']) > 0:
       if self.prefetch:
        self.xbmcitems.add(len(programs))
    return self.xbmcitems.addall()
   else:
    sys.stderr.write("episodes: Couldn't find any videos")
  else:
   sys.stderr.write("episodes: Couldn't get videos webpage")

 def show(self, channel, title): #Show video items from a TV Show style TV3 webpage
  page = webpage("%s/%s/%s/%s" % (self.channels[channel]['base'], self.channels[channel]['shows'], title, "TVOnDemand.aspx"))
  if page.doc:
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   programblock = html_divtag.find(attrs={"class": "grid_8"})
   if programblock:
    programs = programblock.findAll('div', attrs={"class": re.compile(r"\bgrid_4\b")})
    if len(programs) > 0:
     for soup in programs:
      self.xbmcitems.items.append(self._itemshow(channel, title, soup))
     return self.xbmcitems.addall()
   else:
    sys.stderr.write("show: Couldn't find video list")
  else:
   sys.stderr.write("show: Couldn't get index webpage")

 def atoz(self, catid, channel): #Show video items from an AtoZ style TV3 webpage
  page = webpage("%s%s%s" % (self._base_url("tv3"), self.urls["cat"], catid))
  if page.doc:
   a_tag=SoupStrainer('div')
   html_atag = BeautifulSoup(page.doc, parseOnlyThese = a_tag)
   programs = html_atag.findAll(attrs={"class": "wideArticles"})
   if len(programs) > 0:
    for soup in programs:
     item = self._itematoz(soup, channel)
     self.xbmcitems.items.append(item)
     if len(item['urls']) > 0:
      if self.prefetch:
       self.xbmcitems.add(len(programs))
    return self.xbmcitems.addall()
   else:
    sys.stderr.write("atoz: Couldn't find any videos")
  else:
   sys.stderr.write("atoz: Couldn't get videos webpage")

 def search(self, channel, query):
  url = "%s/OnDemand/ShowEpisodesDetail.aspx?MCat=%s" % (self.urls['base'], query)
  page = webpage(url, agent="chrome")
  if page.doc:
   soup = BeautifulSoup(page.doc)
   title = soup.find('h3', attrs={'class' : 'showMcat'}).contents[0].strip()
   print title
   a_tag=SoupStrainer('div')
   html_atag = BeautifulSoup(page.doc, parseOnlyThese = a_tag)
   programs = html_atag.findAll('div', attrs={"class": re.compile(r'\blistWrapper\b')})
   print programs
   if len(programs) > 0:
    for soup in programs:
     item = self._itemsearch(soup, title, "TV3")
     if item:
      self.xbmcitems.items.append(item)
     item = self._itemsearch(soup, title, "Four")
     if item:
      self.xbmcitems.items.append(item)
    return self.xbmcitems.addall()
   else:
    sys.stderr.write("_search: Couldn't find any videos")
  else:
   sys.stderr.write("_search: Couldn't get videos webpage")

 def _itemsearch(self, soup, title, channel): # Scrape items from a table-style HTML page
  baseurl = self._base_url(channel)
  item = tools.xbmcItem(channel, self.channel)
  item['videoInfo']["TVShowTitle"] = title
  url = soup.find('a', attrs={'class' : 'flt_l'})
  if not url:
   return {}
  print url['href']
  # http://www.tv3.co.nz/THE-BLACKLIST-Season-2-Ep-7/tabid/3692/articleID/104035/MCat/3823/Default.aspx

  href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), url['href'])
  if href:
   image = soup.find("img")
   if image:
    item['videoInfo']["Thumb"] = image['src']
   ep = soup.find("div", attrs={"class": 'epDetail'})
   if ep:
    if ep.a:
     item['videoInfo'].update(self._seasonepisode(ep.a))
   synopsis = soup.find('div', attrs={'class' : 'epSynop'})
   if synopsis:
    item['videoInfo']['Plot'] = synopsis.p.contents[0].strip()
   dateDetails = soup.findAll("div", attrs={'class' : 'epDetailData'})
   for detail in dateDetails:
    if detail.time:
     epdate = detail.a.contents[0].strip()
     epdate += " " + str(date.today().year)
     item['videoInfo']['Date'] = epdate
    else:
     duration = detail.a.contents[0].strip()
     parts = duration.split(":")
     dur = 0
     for part in parts:
      dur *= 60
      dur += int(part)
     item['videoInfo']['duration'] = dur
   item.titleplot()
   item['playable'] = True
   item['videoInfo']["FileName"] = "%s?ch=TV3&id=%s&channel=%s&info=%s" % (self.base, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), channel, item.infoencode())
   return item
  return None

 def _itemdiv(self, soup, channel): #Scrape items from a div-style HTML page
  baseurl = self.channels[channel]['base']
  item = tools.xbmcItem(channel, self.channel)
  #item.info["Studio"] = provider
  link = soup.find("a")
  if link:
   href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
   if href:
    showname = soup.find("div", attrs={'class' : 'artTitle'})
    if showname:
     title = showname.a.contents[0].strip()
     if title != "":
      item['videoInfo']["TVShowTitle"] = title
      image = soup.find("img")
      if image:
       item['videoInfo']["Thumb"] = image['src']
      se = soup.find("p")
      if se:
       item['videoInfo'].update(self._seasonepisode(se))
      item.titleplot()
      item['playable'] = True
      item['videoInfo']["FileName"] = "%s?ch=TV3&channel=%s&id=%s&info=%s" % (self.base, channel, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), item.infoencode())
      return item
     else:
      sys.stderr.write("_itemdiv: No title")
    else:
     sys.stderr.write("_itemdiv: No link.string")
   else:
    sys.stderr.write("_itemdiv: No href")
  else:
   sys.stderr.write("_itemdiv: No link")

 def _itemshow(self, channel, title, soup): #Scrape items from a show-style HTML page
  baseurl = self.channels[channel]['base']
  item = tools.xbmcItem(channel, self.channel)
  link = soup.find("a")
  if link:
   if link.has_key('href'):
    href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
    if href:
     showname = link.img['alt']
     title = showname.strip()
     if title != "":
      item['videoInfo']["TVShowTitle"] = title
      image = soup.find("img")
      if image:
       item['videoInfo']["Thumb"] = image['src']
      se = soup.find("h4")
      if se:
       sea = se.find('a')
       if sea:
        item['videoInfo'].update(self._seasonepisode(sea))
      plot = soup.find("p")
      if plot:
       if plot.string:
        item['videoInfo']["PlotOutline"] = plot.string.strip()
      item.titleplot()
      item['playable'] = True
      showid = "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4))
      item['videoInfo']['id'] = showid
      item['videoInfo']["FileName"] = "%s?ch=TV3&channel=%s&id=%s&info=%s" % (self.base, channel, showid, item.infoencode())
      return item
    else:
     #sys.stderr.write("_itemshow: No title")
     pass
   else:
    #sys.stderr.write("_itemshow: No href")
    pass
  else:
   #sys.stderr.write("_itemshow: No link")
   pass
  return {}

 def _itemtable(self, soup, channel, title): #Scrape items from a table-style HTML page
  item = tools.xbmcItem(channel, self.channel)
  link = soup.find('a')
  if link:
   if link.string:
    plot = link.string.strip()
    if plot != "":
     item['videoInfo']["PlotOutline"] = plot
     item['videoInfo']["TVShowTitle"] = title
     item['videoInfo'].update(self._seasonepisode(link))
     item.titleplot()
     href = re.search("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (self._base_url("tv3"), self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
     if href:
      item.playable = True
      item['videoInfo']["FileName"] = "%s?ch=TV3&id=%s&provider=%s&info=%s" % (self.base, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), provider, item.infoencode())
     return item
    else:
     sys.stderr.write("_itemtable: No plot")
   else:
    sys.stderr.write("_itemtable: No link.string")
  else:
   sys.stderr.write("_itemtable: No link")

 def _itematoz(self, soup, channel): #Scrape items from an AtoZ-style HTML page
  baseurl = self._base_url(channel)
  item = tools.xbmcItem(channel, self.channel)
  if soup.find('h5'):
   link = soup.h5.find("a", attrs={"href": re.compile(baseurl)})
   if link:
    infoitems = {}
    href = re.match("%s/(.*?)/%s/([0-9]+)/%s/([0-9]+)/%s/([0-9]+)/" % (baseurl, self.urls["video1"], self.urls["video2"], self.urls["video3"]), link['href'])
    if href:
     if link.string:
      title = link.string.strip()
      if title != "":
       item['videoInfo']["TVShowTitle"] = title
       image = soup.find("img", attrs={"src": re.compile(self.urls["IMG_RE2"]), "title": True})
       if image:
        item['videoInfo']["Thumb"] = image['src']
       item['videoInfo'].update(self._seasonepisode(soup.contents[4]))
       item.titleplot()
       plot = soup.find("span", attrs={"class": "lite"})
       if plot.string:
        cleanedplot = plot.string.strip()
        if cleanedplot:
         item['videoInfo']["Plot"] = item.unescape(cleanedplot)
       item.playable = True
       item['videoInfo']["FileName"] = "%s?ch=%s&id=%s&provider=%s&info=%s" % (self.base, self.channel, "%s,%s,%s,%s" % (href.group(1), href.group(2), href.group(3), href.group(4)), provider, item.infoencode())
       if "FileName" in item['videoInfo'] or len(item.urls) > 0:
        return item
      else:
       sys.stderr.write("_itematoz: No title")
     else:
      sys.stderr.write("_itematoz: No link.string")
    else:
     sys.stderr.write("_itematoz: No href")
   else:
    sys.stderr.write("_itematoz: No link")
  else:
   sys.stderr.write("_itematoz: No h5")

 def play(self, id, channel, encodedinfo):
  item = tools.xbmcItem(channel, self.channel)
  item.infodecode(encodedinfo)
  item['fanart'] = self.xbmcitems.fanart
  item['urls'] = self._geturls(id, channel)
  if item['urls']:
   return self.xbmcitems.resolve(item, self.channel)

 def _geturls(self, id, channel): #Scrape a page for a given OnDemand video and build an RTMP URL from the info in the page, then play the URL
  urls = dict()
  ids = id.split(",")
  if len(ids) == 4:
   pageUrl = "%s/%s/%s/%s/%s/%s/%s/%s/%s" % (self.channels[channel]['base'], ids[0], self.urls["video1"], ids[1], self.urls["video2"], ids[2], self.urls["video3"], ids[3], self.urls["video4"])
   page = webpage(pageUrl)
  else:
   page = webpage(id) # Huh? - I guess this is feeding a full URL via the id variable
  if page.doc:
   videoid = re.search('var video ="/(.*?)/([0-9A-Z\-]+)/(.*?)";', page.doc)
   if videoid:
    #videoplayer = re.search('swfobject.embedSWF\("(http://static.mediaworks.co.nz/(.*?).swf)', page.doc)
    videoplayer = 'http://static.mediaworks.co.nz/video/jw/5.10/df.swf'
    if videoplayer:
     rnd = ""
     auth = re.search('random_num = "([0-9]+)";', page.doc)
     if auth:
      rnd = "?rnd=" + auth.group(1)
     swfverify = ' swfVfy=true swfUrl=%s%s pageUrl=%s' % (videoplayer, rnd, pageUrl)
     realstudio = 'tv3'
     site = re.search("var pageloc='(TV-)?(.*?)-", page.doc)
     if site:
      realstudio = site.group(2).lower()
     playlist = list()
     qualities = [330]
     #if re.search('flashvars.sevenHundred = "yes";', page.doc):
     qualities.append(700)
     #if re.search('flashvars.fifteenHundred = "yes";', page.doc):
     #qualities.append(1500)
     #if not re.search('flashvars.highEnd = "true";', page.doc): # flashvars.highEnd = "true";//true removes 56K option
     # qualities.append(56)
     geo = re.search('var geo= "(.*?)";', page.doc)
     if geo:
      if geo.group(1) == 'geo' or geo.group(1) == 'geomob':
       for quality in qualities:
        urls[quality] = '%s/%s/%s/%s/%s/%s_%sK.mp4' % (self.urls["rtmp1"], self.channels[channel]['rtmp'], self.urls["rtmp2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality) + swfverify
      elif geo.group(1) == 'str':
       for quality in qualities:
        app = ' app=tv3/mp4:transfer' # + videoid.group(1)
        tcurl = ' tcUrl=rtmpe://flashcontent.mediaworks.co.nz:80/'
        playpath = ' playpath=%s/%s_%sK' % (videoid.group(2), videoid.group(3), quality)
        urls[quality] = '%s/%s/%s/%s/%s/%s_%sK' % (self.urls['news1'], "vod", self.urls["rtmp2"] + "3news", videoid.group(1), urllib.quote(videoid.group(2)), urllib.quote(videoid.group(3)), quality) + ' pageUrl=' + pageUrl
    #  elif geo.group(1) == 'no':
    #   for quality in qualities:
    #    urls[quality] = '%s/%s/%s%s/%s/%s_%s.%s' % (self.urls["http1"], "four", self.urls["http2"], videoid.group(1), videoid.group(2), urllib.quote(videoid.group(3)), quality, "mp4")
    else:
     sys.stderr.write("_geturls: No videoplayer")
   else:
    sys.stderr.write("_geturls: No videoid")
  else:
   sys.stderr.write("_geturls: No page.doc")
  return urls

 def _seasonepisode(self, se): #Search a tag for season and episode numbers. If there's an episode and no season, assume that it's season 1
  if se:
   info = dict()
   info["PlotOutline"] = se.contents[0].strip()
   season = re.search("(Cycle|Season) ([0-9]+)", se.contents[0])
   seasonfound = 0
   if season:
    info["Season"] = int(season.group(2))
    seasonfound = 1
   episode = re.search("Ep(|isode) ([0-9]+)", se.contents[0])
   if episode:
    info["Episode"] = int(episode.group(2))
    if not seasonfound:
     info["Season"] = 1
   return info

 def _dateduration(self, ad): #Search a tag for aired date and video duration
  if ad:
   info = dict()
   aired = re.search("([0-9]{2}/[0-9]{2}/[0-9]{2})", ad.contents[1])
   if aired:
    info["Premiered"] = tools.xbmcdate(aired.group(1))
    info["Date"] = info["Premiered"]
   duration = re.search("\(([0-9]+:[0-9]{2})\)", ad.contents[1])
   if duration:
    info["Duration"] = time.strftime("%M", time.strptime(duration.group(1), "%M:%S"))
   return info

 def _base_url(self, provider): #Build a base website URL for a given site (four or tv3)
  return "%s.%s.%s" % (self.urls['base1'], provider.lower(), self.urls['base2'])

 def _rtmpchannel(self, provider):
  if provider == "four":
   return "c4"
  return provider
