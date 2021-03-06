#/*
# *   Copyright (C) 2010 Mark Honeychurch
# *   based on the TVNZ Addon by JMarshall
# *
# *
# * This Program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2, or (at your option)
# * any later version.
# *
# * This Program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; see the file COPYING. If not, write to
# * the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# * http://www.gnu.org/copyleft/gpl.html
# *
# */

#ToDo:
# Fix sorting methods (they don't all seem to work properly)
# Scan HTML data for broadcast dates (in AtoZ, table view, etc)
# Find somewhere to add expiry dates?
# Add an option to show an advert before the program (I can't find the URLs for adverts at the moment)

#Useful list of categories
# http://ondemand.tv3.co.nz/Host/SQL/tabid/21/ctl/Login/portalid/0/Default.aspx

#XBMC Forum Thread
# http://forum.xbmc.org/showthread.php?t=37014


# Import external libraries

import os, cgi, sys, urlparse, urllib
#import xbmcaddon, xbmcgui, xbmcplugin

import resources.tools as tools
import resources.config as config

#tools.initaddon()

settings = config.__settings__


def tv3():
 from resources.channels.tv3 import tv3 as tv3class
 tv3 = tv3class()
 ret = []
 if params.get("channel", "") != "":
  if params.get("cat", "") != "":
   if params["cat"][0] == "shows":
    ret = tv3.shows(params["channel"][0])
   elif params["cat"][0] == "show":
    ret = tv3.show(params["channel"][0], params["title"][0])
   elif params["cat"][0] == "search":
    ret = tv3.search(params["channel"][0], params['q'][0])
   else:
    ret = tv3.episodes(params["channel"][0], params["cat"][0])
  elif params.get("id", "") != "":
   ret = tv3.play(params["id"][0], params["channel"][0], params["info"][0])
  else:
   ret = tv3.channelindex(params["channel"][0])
 else:
  if config.__settings__.get('TV3', 'folders') == 'True':
   ret = tv3.index()
  else:
   ret = tv3.index(False)
 return ret

def tvnz():
 from resources.channels.tvnz import tvnz as tvnzclass
 tvnz = tvnzclass()
 ret = []
 if params.get("info", "") != "":
  ret = tvnz.play(params["id"][0], params["info"][0])
 elif not "type" in params:
  ret = tvnz.index()
 else:
  if params["type"][0] == "shows":
   ret = tvnz.episodes(params["id"][0])
  elif params["type"][0] == "singleshow":
   ret = tvnz.episodes(params["id"][0])
  elif params["type"][0] == "alphabetical":
   ret = tvnz.show(params["id"][0])
  elif params["type"][0] == "distributor":
   tvnz.SHOW_DISTRIBUTORS(params["id"][0])
   ret = tools.addsorting(["label"], "tvshows")
  elif params["type"][0] == "search":
   ret = tvnz.search(params['q'][0])
 return ret

# Website states "new website coming soon as of 11/2/2014
#
#def choicetv():
# from resources.channels.choicetv import choicetv as choicetvclass
# choicetv = choicetvclass()
# if params.get("type", "") != "":
#  ret = choicetv.index(params["type"][0], params["id"][0])
# elif params.get("view", "") != "":
#  ret = choicetv.play(params["view"][0])
# else:
#  ret = choicetv.index()
# return ret

def ziln():
 from resources.channels.ziln import ziln as zilnclass
 ziln = zilnclass()
 ret = []
 if params.get("folder", "") != "":
  if params["folder"][0] == "channels":
   ret = ziln.programmes("channel", "")
  elif params["folder"][0] == "search":
   ret = ziln.search(params['q'][0])
 elif params.get("channel", "") != "":
  ret = ziln.programmes("video", params["channel"][0])
 elif params.get("video", "") != "":
  ret = ziln.play(params["video"][0], params["channelNum"][0])
 else:
  ret = ziln.index()
 return ret

def nzonscreen():
 from resources.channels.nzonscreen import nzonscreen as nzonscreenclass
 nzonscreen = nzonscreenclass()
 ret = []
 if params.get("filter", "") != "":
  if params["filter"][0] == "search":
   if params.get("page", "") != "":
    ret = nzonscreen.search(params['q'][0], params["page"][0])
   else:
    ret = nzonscreen.search(params['q'][0])
  elif params.get("page", "") != "":
   ret = nzonscreen.page(urllib.unquote(params["filter"][0]), params["page"][0])
  else:
   ret = nzonscreen.index(urllib.unquote(params["filter"][0]))
 elif params.get("title", "") != "":
  ret = nzonscreen.play(params["title"][0], params["info"][0])
 else:
  ret = nzonscreen.index()
 return ret

def stuff():
 from resources.channels.stuff import stuff as stuffclass
 stuff = stuffclass()
 ret = []
 if params.get("type", "") != "":
  ret = stuff.index(params["type"][0], params["id"][0])
 elif params.get("id", "") != "":
  ret = stuff.play(params["section"][0], params["id"][0])
 elif params.get("section", "") != "":
  ret = stuff.sections(params["section"][0])
 else:
  ret = stuff.index()
 return ret


# Decide what to run based on the plugin URL

params = cgi.parse_qs(urlparse.urlparse(sys.argv[2])[4])
if params:
 if params.get("item", "") != "":
  xbmcitems = tools.xbmcItems()
  xbmcitems.decode(params["item"][0])
 else:
  if params["ch"][0] == "TV3":
   print tv3()
  elif params["ch"][0] == "TVNZ":
   print tvnz()
#  elif params["ch"][0] == "ChoiceTV":
#   print choicetv()
  elif params["ch"][0] == "Ziln":
   print ziln()
  elif params["ch"][0] == "NZOnScreen":
   print nzonscreen()
  elif params["ch"][0] == "Stuff":
   print stuff()
# elif params["ch"][0] == "iSKY":
# https://www.skytv.co.nz/skyid/rest/login?skin=isky
# POST:
# email
# password
# elif params["ch"][0] == "Quickflix":
# https://secure.quickflix.co.nz/Partial/Secure/Standard/Login
# POST:
# LoginEmail
# LoginPassword
# elif params["ch"][0] == "IGLOO":
  elif params["ch"][0] == "Prime":
   from resources.channels.prime import prime as primeclass
   prime = primeclass()
   print prime.get()
  else:
   sys.stderr.write("Invalid Channel ID")
else:
 channels = dict()
 channels["TV3"] = "Latest TV On Demand video from both TV3 and FOUR."
 channels["TVNZ"] = "Ready when you are."
 channels["Prime"] = "Prime News: First At 5:30 brings you the top news and sports stories from New Zealand and around the world."
 channels["NZOnScreen"] = "The online showcase of New Zealand television, film and music video."
 channels["Ziln"] = "Ziln links the audience reach of broadband internet with a potentially limitless amount of targetted live streaming and View On Demand TV/video content."
# channels["ChoiceTV"] = "Choice TV's programming centres on entertainment, information and lifestyle content from around the world."
 channels["Stuff"] = "Stuff covers every aspect of news and information, from breaking national and international crises through to in-depth features, sports, business, entertainment and technology articles, weather reports, travel services, movie reviews, rural news... and lots more."
 xbmcitems = tools.xbmcItems()
 for channel, description in channels.iteritems():
  if not settings.get(channel, 'hide') == "True":
   item = tools.xbmcItem()
   item['fanart'] = os.path.join('extrafanart', "%s.jpg" % channel)
   item['videoInfo']["Title"] = channel
   item['videoInfo']["Thumb"] = os.path.join(config.__path__, "resources/images/%s.png" % channel)
   item['videoInfo']["Plot"] = description
   item['videoInfo']["FileName"] = "%s?ch=%s" % (sys.argv[0], channel)
   xbmcitems.items.append(item)
 print xbmcitems.addall()

