import urllib, re, sys
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulStoneSoup

import resources.tools as tools
import resources.config as config
settings = config.__settings__
from resources.tools import webpage

class nzonscreen:
 def __init__(self):
  self.base = sys.argv[0]
  self.channel = "NZOnScreen"
  self.urls = dict()
  self.urls['base'] = 'http://www.nzonscreen.com'
  self.urls['json'] = '/html5/video_data/'
  self.urls['metadata'] = '/title/'
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

 def index(self, filter = "/explore/"):
  filterarray = filter.strip('/').split('/')
  filterlevel = len(filterarray)
  print filter
  print filter.strip('/')
  print str(filterlevel)
  url = self.urls['base'] + filter
  #sys.stderr.write("URL: " + url)
  #sys.stderr.write('explore_filter_%s' % str(filterlevel))
  page = webpage(url, 'chrome', 'nzos_html5=true')
  #page = webpage(self.urls['base'])
  if page.doc:
   #resources.tools.gethtmlpage("http://www.nzonscreen.com/html5/opt_in", "chrome", 1) # Get a cookie for this session to enable the HTML5 video tag
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   sections = html_divtag.find(attrs={'id' : 'explore_filter_%s' % str(filterlevel)})
   if not sections:
    sections = html_divtag.find(attrs={'id' : 'explore_listview'})
   if sections:
    links = sections.findAll('a')
    if len(links) > 0:
     for link in links:
 #     if link.string:
 #     sys.stderr.write(link.contents[0].string)
      item = tools.xbmcItem(self.channel)
      info = item['videoInfo']
      info["FileName"] = "%s?ch=%s&filter=%s" % (self.base, self.channel, urllib.quote(link["href"]))
      #info["Title"] = link.contents[0].string.strip()
      if link.string:
       info["Title"] = link.string.strip()
      else:
       filterarray = link["href"].split('/')
       info["Title"] = filterarray[len(filterarray) - 1].capitalize()
 #     info["Thumb"] =
      self.xbmcitems.items.append(item)
     if filterlevel == 1:
      item = tools.xbmcItem(self.channel)
      info = item['videoInfo']
      info["FileName"] = "%s?ch=%s&filter=search" % (self.base, self.channel)
      info["Title"] = "Search"
      self.xbmcitems.items.append(item)
    else:
 #    if filterarray[filterlevel] ==
     nav = html_divtag.find(attrs={'class' : 'nav_pagination'})
     if nav:
      pages = nav.findAll('a')
      if pages:
       for page in pages:
        if page.string:
         lastpage = page.string.strip()
         #url = page['href']
       for i in range(1, int(lastpage)):
        item = tools.xbmcItem(self.channel)
        info = item['videoInfo']
        info["FileName"] = "%s?ch=%s&filter=%s&page=%s" % (self.base, self.channel, urllib.quote(filter), str(i))
        info["Title"] = 'Page %s' % str(i)
        self.xbmcitems.items.append(item)
    return self.xbmcitems.addall()
   else:
    sys.stderr.write("index: No sections")
  else:
   sys.stderr.write("index: No page.doc")

 def page(self, filter, page):
  url = "%s%s?page=%s" % (self.urls['base'], filter, page)
  page = webpage(url, 'chrome', 'nzos_html5=true')
  if page.doc:
   div_tag = SoupStrainer('div')
   html_divtag = BeautifulSoup(page.doc, parseOnlyThese = div_tag)
   results = html_divtag.find(attrs={'id' : 'filter_result_set'})
   if results:
    rows = results.findAll('tr')
    if len(rows) > 0:
     for row in rows:
      cells = row.findAll('td')
      count = len(cells)
      if count > 0:
       item = tools.xbmcItem(self.channel)
       for cell in cells:
        if cell['class'] == 'image':
	 src = cell.div.div.a.img['src']
         if not src.startswith("http://"):
          src = self.urls['base'] + src
         item['videoInfo']['Thumb'] = src
         title = re.search("/title/(.*)", cell.a['href'])
         if not title:
          title = re.search("/interviews/(.*)", cell.a['href'])
        elif cell['class'].startswith('title_link'):
         item['videoInfo']['Title'] = item.unescape(cell.a.contents[0])
        elif cell['class'] == 'added':
         item['videoInfo']["Date"] = tools.xbmcdate(cell.contents[0], ".")
       if title:
        item['videoInfo']["FileName"] = "%s?ch=%s&title=%s&info=%s" % (self.base, self.channel, title.group(1), item.infoencode())
        item['playable'] = True
        if not title.group(1).endswith("/series"):
         self.xbmcitems.items.append(item)
     return self.xbmcitems.addall()
    else:
     sys.stderr.write("page: No rows")
   else:
    sys.stderr.write("page: No results")
  else:
   sys.stderr.write("page: No page.doc")

# def search(self):
#  import xbmc
#  keyboard = xbmc.Keyboard("", "Search for a Video")
#  #keyboard.setHiddenInput(False)
#  keyboard.doModal()
#  if keyboard.isConfirmed():
#   return self.page("search", keyboard.getText())

 def play(self, title, encodedinfo):
  item = tools.xbmcItem(self.channel)
  item.infodecode(encodedinfo)
  item['units'] = "MB"
  item['fanart'] = self.xbmcitems.fanart
  item['urls'] = self._geturls(title)
  item['videoInfo'].update(self._getMetadata(title))
  return self.xbmcitems.resolve(item, self.channel)

 def _getMetadata(self, title):
  metadata = {}
  url = "%s%s%s" % (self.urls['base'], self.urls['metadata'], title)
  page = webpage(url)
  if page.doc:
   soup = BeautifulSoup(page.doc)
   synopsisDiv = soup.find("div", attrs={'id' : 'widget_title_synopsis'})
   try:
    synopsis = [ str(item) for item in synopsisDiv.div.p.contents ]
    metadata['PlotOutline'] = " ".join(synopsis).strip()
   except Exception:
    pass
   metadata['id'] = title
  return metadata

 def _geturls(self, title):
  url = "%s%s%s" % (self.urls['base'], self.urls['json'], title)
  page = webpage(url)
  returnurls = dict()
  if page.doc:
   import json
   videos = json.loads(page.doc)
   allurls = dict()
   filesizes = dict()
   video = videos[0]
   for vidFormat, items in video.iteritems():
    if type(items) is not dict:
     continue
    allurls[vidFormat] = dict()
    filesizes[vidFormat] = dict()
    for name, value in items.iteritems():
     if name[-4:] == '_res':
      bitrate = name[:-4]
      if not bitrate in allurls[vidFormat]:
       allurls[vidFormat][bitrate] = list()
      if not bitrate in filesizes[vidFormat]:
       filesizes[vidFormat][bitrate] = 0
      allurls[vidFormat][bitrate].append(video[vidFormat][bitrate + '_res'])
      filesizes[vidFormat][bitrate] += video[vidFormat][bitrate + '_res_mb']

   for vidFormat, bitrates in allurls.iteritems():
    for bitrate, urls in bitrates.iteritems():
     size = filesizes[vidFormat][bitrate]
     if not size in returnurls:
      returnurls[size] = list()
     returnurls[size].extend(urls)
  return returnurls

