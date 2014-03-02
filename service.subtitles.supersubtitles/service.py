# -*- coding: utf-8 -*- 

import os
import sys
import xbmc
import shutil
import urllib
import xbmcvfs
import xbmcaddon
import xbmcgui,xbmcplugin,shutil

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp') ).decode("utf-8")

if xbmcvfs.exists(__temp__):
  shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

sys.path.append (__resource__)

from SSUtilities import log, normalizeString, search_subtitles, download_subtitles

def Search( item): 
  subtitles_list = search_subtitles(item['file_original_path'], item['title'], item['tvshow'], item['year'], item['season'], item['episode'], item['temp'], item['rar'], item['3let_language'][0], 'eng', 'hun', item['stack']) 

  if subtitles_list:
    for it in subtitles_list:
      listitem = xbmcgui.ListItem(label=it["eng_language_name"],
                                  label2=it["filename"],
                                  iconImage=it["rating"],
                                  thumbnailImage= it["language_flag"] 
                                  )
      listitem.setProperty( "sync", ("false", "true")[it["sync"]] )
      listitem.setProperty( "hearing_imp", ("false", "true")[it.get("hearing_imp", False)] )
      
      url = "plugin://%s/?action=download&link=%s&ID=%s&filename=%s" % (__scriptid__,
                                                                        it["link"],
                                                                        it["ID"],
                                                                        it["filename"]
                                                                        )
      
      xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)

   
def get_params(string=""):
  param=[]
  if string == "":
    paramstring=sys.argv[2]
  else:
    paramstring=string 
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
                                
  return param

params = get_params()

if params['action'] == 'search':
  log( __name__, "action 'search' called")
  item = {}
  item['temp']               = False
  item['rar']                = False
  item['stack']              = False
  item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
  item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
  item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
  item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
  item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))# try to get original title
  item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))# Full path of a playing file
  item['3let_language']      = [] #['scc','eng']
  
  for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
    clang = xbmc.convertLanguage(lang,xbmc.ISO_639_2);
    log(__name__, "lang: %s, clang: %s" % (lang, clang))
    item['3let_language'].append(lang)
  
  if item['title'] == "":
    log( __name__, "VideoPlayer.OriginalTitle not found")
    item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title
    
  if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
    item['season'] = "0"                                                          #
    item['episode'] = item['episode'][-1:]
  
  if ( item['file_original_path'].find("http") > -1 ):
    item['temp'] = True

  elif ( item['file_original_path'].find("rar://") > -1 ):
    item['rar']  = True
    item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

  elif ( item['file_original_path'].find("stack://") > -1 ):
    item['stack']  = True
    stackPath = item['file_original_path'].split(" , ")
    item['file_original_path'] = stackPath[0][8:]
  
  Search(item)
	
elif params['action'] == 'download':
  download_subtitles('', '', 'zip',__temp__,'sub_folder', 'session_id')
  subs = Download(url,params["filename"])
  for sub in subs:
    listitem = xbmcgui.ListItem(label=sub)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)
  

elif params['action'] == 'manualsearch':
  xbmc.executebuiltin(u'Notification(%s,%s,2000,%s)' % 
                                      (__scriptname__,
                                       __language__(32004),
                                       os.path.join(__cwd__,"icon.png")
                                     )
                      )
  
xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
  
  
  
  
  
  
  
  
    
