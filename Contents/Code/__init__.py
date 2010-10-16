# -*- coding: utf-8 -*-
# Writen by me, yeah! Grigory Bakunov <thebobuk@ya.ru>
# Please leave my copyrights here cause as you can notice
# "Copyright" always means "absolutely right copying".
# Illegal copying of this code prohibited by real patsan's law!

from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re
from copy import deepcopy
####################################################################################################

VIDEO_PREFIX = "/video/ruhdtv"

SITE = "http://ruhd.tv/"
S_SERIES = SITE + "ShowSeries/"
S_SERIES_XML = S_SERIES + "XML/"
S_EPISODES = SITE +"ShowEpisodes/"
S_EPISODES_XML = S_EPISODES + "%s/XML/"
S_FULLPATH = SITE + 'GetEpisodeLink/'
S_FULLPATH_XML = S_FULLPATH + '%s/XML/'
S_RSS_PATH = SITE + "ShowRSS/"
NAME = L('Title')

ART           = 'art-tv.png'
ICON          = 'icon-tv.png'

####################################################################################################

__authed = False

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def CreatePrefs():
    Prefs.Add(id='username', type='text', default='', label='Username')
    Prefs.Add(id='password', type='text', default='', label='Password', option='hidden')

def ValidatePrefs(suspendOk=False):
    u = Prefs.Get('username')
    p = Prefs.Get('password')
    if( u and p ):
        return True if Authentificate(u, p) else MessageContainer("Error", "Wrong username or password")
    else:
        return MessageContainer( "Error",   "You need to provide both a user and password" )

def Authentificate(user, passwd):
    global __authed
    if __authed:
        return True
    req = HTTP.Request(SITE, values={"login": user, "password": passwd})
    if "<form" in str(req):
        Log("Oooops, wrong pass or no creds")
        return False
    Log("Ok, i'm in!")
    __authed = True
    return True

def FetchXML(url):
    try:
        xml = XML.ElementFromURL(url)
    except:
        Log('Need auth or bad xml')
        xml = None
    if xml is None or str(xml.tag) != 'document':
        f = Authentificate(Prefs.Get('username'), Prefs.Get('password'))
        if not f:
            return None
        xml = XML.ElementFromURL(url)
    return xml

def noHTML(text):
    return text.replace('<br />','\n').replace('<br/>', '\n')\
               .replace('&ndash;',u'\u2013')\
               .replace('&mdash;',u'\u2014')\
               .replace('&raquo;','»').replace('&laquo;', '«')\
               .replace('&quot;', '"')\
               .replace('&hellip;', '…')\
               .replace('<span style="font-weight: bold;">', '«')\
               .replace('</span>', '»') if text else text
               

def _ig(xml, tid, default = None):
    try:
        return xml.xpath(tid)[0].text
    except:
        return default

class Video:
    def __init__(self, ids, xml):
        xml = xml.xpath('//item')[0]
        self.ids = ids
        self.snd = [_ig(xml,'./defsnd'), _ig(xml, './addsnd')]
        self.sub = [_ig(xml,'./sub1'),   _ig(xml,'./sub2')   ]
        self.vurl = _ig(xml, './vurl')
        self.url = SITE + 'content/' + self.vurl

class Episode:
    def __init__(self, mark, xml):
        self.mark   = mark
        self.title  = _ig(xml, './title')
        self.etitle = _ig(xml, './etitle')
        self.info   = noHTML(_ig(xml, './info'))
        self.ids    = _ig(xml, './id_episodes')
        self.snum   = int(_ig(xml, './snum'))
        self.enum   = int(_ig(xml, './enum'))
        self.vnum   = _ig(xml, './vnum')
        self.thumb  = SITE + 'content/%s/sc/%.2d-%.2d' % (mark, self.snum, self.enum)

    def __repr__(self):
        return '%s > %s s%de%s (%s)' % ( self.mark, self.title, self.snum, self.vnum, self.ids)
    
    def __str__(self):
        return self.__repr__()

class Serial:
    def __init__(self, xml):
        self.title  = _ig(xml, './title')
        self.etitle = _ig(xml, './etitle')
        self.info   = noHTML( _ig(xml, './info') )
        self.ids    = _ig(xml, './id_series')
        self.mark   = _ig(xml, './mark')
        self.thumb  = _ig(xml, './fpimg')
        self.art    = _ig(xml, './pimg')

    def __repr__(self):
        return '%s/%s (%s/%s)' % ( self.title, self.etitle, self.ids, self.mark)

    def __str__(self):
        return self.__repr__()

def FetchSeriesList(favs=False):
    sv = {}
    serieslist = []
    favorites  = []
    xml = FetchXML(S_SERIES_XML)
    if xml is None:
        return None
    for item in xml.xpath('//document/fp/serieslist/item'):
        serial = Serial(item)
        serieslist.append(serial)
        sv[serial.ids] = serial
    serieslist.sort(lambda x,y: -1 if x.title < y.title else 1)
    if favs:
        for item in xml.xpath('//document/favorites/item/series'):
            favorites.append(sv[item.text])
        return favorites
    return serieslist

def FetchRSSEpisodesList():
    rsslist = []
    xml = RSS.FeedFromURL(S_RSS_PATH)
    if xml is None:
        return None
    for item in xml.entries:
        ids = item.link.split('/')[4]
        rsslist.append((ids, item.title))
    return rsslist
    
def FetchEpisodesList(ids, mark):
    episodeslist = []
    xml = FetchXML(S_EPISODES_XML % ids)
    if xml is None:
        return None
    for item in xml.xpath('/document/series/season/item'):
        episodeslist.append(Episode(mark, item))
    return episodeslist

def FetchVideoItem(ids):
    xml = FetchXML(S_FULLPATH_XML % ids)
    if xml is None:
        return None
    return Video(ids, xml)

def Series(sender, ids, mark, title, art):
    mc = MediaContainer()
    series = FetchEpisodesList(ids, mark)
    if series is None:
        return MessageContainer("Error", "Can't do that.\nCheck preferences or refill your ballance!")
    for seria in series:
        mc.Append(
            Function(
                VideoItem(
                    Videos,
                    "%d.%d. %s" %(seria.snum, seria.enum, seria.title),
                    art = art,
                    thumb = seria.thumb
                    ),
                ids = seria.ids))
    return mc

def Videos(sender, ids):
    v = FetchVideoItem(ids)
    if v is None:
        return MessageContainer("Error", "Can't do that.\nCheck preferences or refill your ballance!")
    return Redirect(v.url)

def Serials(sender, favs = False):
    mc = MediaContainer(viewGroup="InfoList")
    serials = FetchSeriesList(favs)
    if serials is None:
        return MessageContainer("Error", "Can't do that.\nCheck preferences or refill your ballance!")
    for item in serials:
        mc.Append(
            Function(
                DirectoryItem(
                    Series,
                    title = item.title,
                    subtitle = item.etitle,
                    summary = item.info,
                    thumb = SITE + item.thumb,
                    art = SITE + item.art),
                ids  = item.ids,
                mark = item.mark,
                title = SITE + item.title,
                art = SITE + item.art))
    return mc

def Updates(sender):
    mc = MediaContainer()
    series = FetchRSSEpisodesList()
    if series is None:
        return MessageContainer("Error", "Can't do that.\nCheck preferences or refill your ballance!")
    for (ids, title) in series:
        mc.Append(
            Function(
                VideoItem(
                    Videos,
                    title,
                    ),
                ids = ids))
    return mc
    

def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")
    if Authentificate(Prefs.Get('username'), Prefs.Get('password')):
        dir.Append(
            Function(
                DirectoryItem(Serials,
                          title='All serials',
                          subtitle = 'List of all shows on this site',
                          thumb=R(ICON)),
                favs = False))
        dir.Append(
            Function(
                DirectoryItem(Serials,
                              title='Favorites',
                              subtitle = 'List of your favorite shows',
                              thumb=R(ICON)),
                favs = True))
        dir.Append(Function(
                DirectoryItem(Updates,
                              title = "Updates",
                              subtitle = 'List of new or updated series',
                              thumb = R(ICON)
                )))
    else:
        Log('No auth!')
    dir.Append(
        PrefsItem(
            title="Preferences",
            subtile="So you can set preferences",
            summary="lets you set preferences",
            thumb=R(ICON)))
    return dir
