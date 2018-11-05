# -*- coding: utf-8 -*-
# Author: Captain N

import re
import os     
import sys
import urllib
import urllib2
import urlparse    
import xbmc         
import xbmcaddon 
import xbmcgui    
import xbmcplugin 
import json
import datetime

from urllib2 import Request 
from urllib2 import urlopen

import downloader
from resources.lib.lists.companies import companies
from resources.lib.lists.networks import networks
from resources.lib.lists.movie_genres import movie_genres
from resources.lib.lists.tv_genres import tv_genres
from resources.lib.lists.movie_years import movie_years
from resources.lib.lists.tv_years import tv_years
from resources.lib.lists.movie_languages import movie_languages
from resources.lib.lists.tv_languages import tv_languages

#########################################
# URL Variables
#########################################

#### TMDB API Key
TMDB_URL = 'https://api.themoviedb.org/3/'
TMDB_API_KEY = "?api_key=d41fd9978486321b466e29bfec203902"

#### TMDB API Variables
POSTER = "https://image.tmdb.org/t/p/w500"
FANART =  "https://image.tmdb.org/t/p/w500"
BACKDROP = "https://image.tmdb.org/t/p/original"
PREVIEW = "https://image.tmdb.org/t/p/preview"

#### TMDB URLS
#Movies
TMDB_MOVIES= 'https://api.themoviedb.org/3/movie/'
TRENDING_MOVIES = "http://api.themoviedb.org/3/discover/movie"+TMDB_API_KEY+"&sort_by=primary_release_date.desc&page=1&vote_count.gte=100"	
POPULAR_MOVIES = "https://api.themoviedb.org/3/movie/popular"+TMDB_API_KEY+"&language=en-US"
TOP_RATED_MOVIES = "https://api.themoviedb.org/3/movie/top_rated"+TMDB_API_KEY+"&language=en-US"
NOW_PLAYING_MOVIES = "https://api.themoviedb.org/3/movie/now_playing"+TMDB_API_KEY+"&language=en-US"
UPCOMING_MOVIES = "https://api.themoviedb.org/3/movie/upcoming"+TMDB_API_KEY+"&language=en-US"
COMPANIES = "https://api.themoviedb.org/3/discover/movie"+TMDB_API_KEY+"&language=en-US&sort_by=popularity.desc&with_companies="
MOVIE_GENRES = "https://api.themoviedb.org/3/discover/movie"+TMDB_API_KEY+"&language=en-US&sort_by=popularity.desc&with_genres="
MOVIE_YEARS = "https://api.themoviedb.org/3/discover/movie"+TMDB_API_KEY+"&language=en-US&sort_by=popularity.desc&primary_release_year="
LANGUAGES_MOVIES = "https://api.themoviedb.org/3/discover/movie"+TMDB_API_KEY+"&release_date.gte=2010&without_genres=16%2C35%2C10751%2C10402%2C&sort_by=popularity.desc&with_original_language="
SEARCH_MOVIES = "https://api.themoviedb.org/3/search/movie"+TMDB_API_KEY+"&language=en-US&query="
SEARCH_KEYWORDS_MOVIES = "https://api.themoviedb.org/3/discover/movie"+TMDB_API_KEY+"&with_keywords="

#TVSHOWS
TMDB_TVSHOWS = "https://api.themoviedb.org/3/tv/"
TRENDING_TVSHOWS = "http://api.themoviedb.org/3/discover/tv"+TMDB_API_KEY+"&vote_count.gte=100&sort_by=first_air_date.desc&page="
POPULAR_TVSHOWS = "https://api.themoviedb.org/3/tv/popular"+TMDB_API_KEY+"&language=en-US&page="
TOP_RATED_TVSHOWS = "https://api.themoviedb.org/3/tv/top_rated"+TMDB_API_KEY+"&language=en-US&page="
ON_THE_AIR_TVSHOWS = "https://api.themoviedb.org/3/tv/on_the_air"+TMDB_API_KEY+"&language=en-US"
AIRING_TVSHOWS = "https://api.themoviedb.org/3/tv/airing_today"+TMDB_API_KEY+"&language=en-US"
NETWORKS = "https://api.themoviedb.org/3/discover/tv"+TMDB_API_KEY+"&language=en-US&sort_by=popularity.desc&include_null_first_air_dates=false&with_networks="
TV_GENRES = "https://api.themoviedb.org/3/discover/tv"+TMDB_API_KEY+"&language=en-US&sort_by=popularity.desc&include_null_first_air_dates=false&with_genres="
TVSHOWS_YEARS = "https://api.themoviedb.org/3/discover/tv"+TMDB_API_KEY+"&language=en-US&sort_by=popularity.desc&include_null_first_air_dates=false&first_air_date_year="
LANGUAGES_TVSHOWS = "https://api.themoviedb.org/3/discover/tv"+TMDB_API_KEY+"&first_air_date.gte=2010&without_genres=10762%2C16%2C10751%2C10764%2C10766%2C10767&sort_by=popularity.desc&include_null_first_air_dates=false&with_original_language="
SEARCH_TVSHOWS = "https://api.themoviedb.org/3/search/tv"+TMDB_API_KEY+"&language=en-US&query="
SEARCH_KEYWORDS_TV = "https://api.themoviedb.org/3/discover/tv"+TMDB_API_KEY+"&with_keywords="



#########################################
# Global Variables
#########################################

#Addon Variables
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon_id  = xbmcaddon.Addon().getAddonInfo('id') 
selfAddon = xbmcaddon.Addon(id=addon_id)
DefaultIcon = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.tmdbwalls', 'icon.png'))
DefaultFanart = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.tmdbwalls', 'fanart.png'))
xbmcplugin.setContent(addon_handle, 'Movies')

#GUI Variables
dialog  = xbmcgui.Dialog()  
dp = xbmcgui.DialogProgress()  
dpBG = xbmcgui.DialogProgressBG()

#Settings Variables
backupdir	=	unicode(selfAddon.getSetting('wallpaper_path'))   
download_dir     =  xbmc.translatePath(os.path.join(backupdir,''))

#########################################
# Directory Functions
#########################################

#Build a URL
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

#Create a List Item
def list_item( listname, icon):
    return xbmcgui.ListItem( listname, iconImage=icon)

#Add a Directory
def addDir(url, li, isFolder):
    return xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=isFolder)

#End of Directory
def endDir():
    return xbmcplugin.endOfDirectory(addon_handle)

#Movies Dir
def createMovieDir(categories):
    for i in categories:
        title =  i

        url = build_url({'mode': 'Movies', 'title': title})
        li = list_item(title, DefaultIcon)
        li.setArt({'thumb': DefaultIcon, 'icon': DefaultIcon, 'poster': DefaultIcon, 'fanart': DefaultFanart, 'landscape': DefaultFanart })
        addDir(url, li, True)
 
    endDir()

#TV Show Dir
def createTVShowDir(categories):
    for i in categories:
        title =  i

        url = build_url({'mode': 'TV Shows', 'title': title})
        li = list_item(title, DefaultIcon)
        li.setArt({'thumb': DefaultIcon, 'icon': DefaultIcon, 'poster': DefaultIcon, 'fanart': DefaultFanart, 'landscape': DefaultFanart })
        addDir(url, li, True)
 
    endDir()

#Create Sub Directories
def createSubDir(categories):
    for i in categories:
        title =  i[0]
        dir_url = i[1]
        dir_type = i[2]

        url = build_url({'mode': 'SubDir', 'title': title, 'dir_url': dir_url, 'dir_type': dir_type})
        li = list_item(title, DefaultIcon)
        li.setArt({'thumb': DefaultIcon, 'icon': DefaultIcon, 'poster': DefaultIcon, 'fanart': DefaultFanart, 'landscape': DefaultFanart })
        addDir(url, li, True)

    endDir()

#########################################
# Search Functions
#########################################

#Get Search Term
def getSearchTerm():
    keyboard = xbmc.Keyboard('default', 'heading')
    keyboard.setDefault('')
    keyboard.setHeading('Search The Movie Database ..')
    keyboard.setHiddenInput(False)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        search_term  = keyboard.getText()
        return (search_term)
    else:
        return 

#########################################
# Downloader - CREDIT: Schism
#########################################

def downloadWallpapers(name,url):
	try:
		if not os.path.exists(download_dir): os.makedirs(download_dir)
	except:pass
	title = name
	name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	name = title + "_" + name + ".jpg"
	path = download_dir
	dp = xbmcgui.DialogProgress()
	lib=os.path.join(path, name)
	dp.create("TMDB Walls","Downloading ..",'', 'Please Wait ..')		
	downloader.download(url, lib, dp)
	dialog.ok('TMDB Walls','Download Complete')

#########################################
# TMDB Info
#########################################

def get_tmdb_info(tmdb_url, page):

    #Page url
    page_url = "&page="+str(page)

    #Open and Read the Response
    request = Request(tmdb_url+page_url)
    response_body = urlopen(request).read()
    response =  str(response_body)
    response = json.loads(response_body)
    results = response['results']

    #Iterate Results
    for result in results:
        try: tmdb_id = str(result['id'])  
        except:   tmdb_id = ''
        try: plot = str(result['overview'])
        except: plot = 'Not Available'
        try: poster = str(POSTER+result['poster_path'])  
        except: poster = ''
        try: fanart = str(FANART+result['backdrop_path'])  
        except: fanart = ''
        try: rating = str(result['vote_average'])
        except: rating = ''

        #Check Mediatype
        try: adult =str(result['adult'])
        except: adult = ''
        if not adult == '':
            mediatype = 'movie'
            try: title = str(result['title'])  
            except: title = ''
            try: premiered = str(result['release_date'])  
            except: premiered = ''
        else:
            mediatype = 'tvshow'
            try: title = str(result['name'])
            except: title = ''
            try: premiered = str(result['first_air_date'])
            except: premiered = ''



        #Build URL
        url = build_url({'mode': 'Result', 'tmdb_id': tmdb_id, 'mediatype': mediatype, 'title': title, "plot": plot, 'poster': poster})
        li = list_item( title, poster)
        li.setInfo(type='video', infoLabels={'mediatype': mediatype, 'title': title, 'plot': plot, 'premiered': premiered, 'rating': rating})
        li.setArt({'thumb': poster, 'icon': poster, 'poster': poster, 'fanart': fanart, 'landscape': fanart })
        addDir(url, li, True)
    
    #Page Control
    page = int(page)
    page += 1
    url = build_url({'mode': 'Next Page', 'tmdb_url': tmdb_url, 'page': page})
    li = list_item('Next Page', DefaultIcon)
    li.setArt({'thumb': DefaultIcon, 'icon': DefaultIcon, 'poster': DefaultIcon, 'fanart': DefaultFanart, 'landscape': DefaultFanart })
    addDir(url, li, True)

    endDir()

#########################################
# TMDB Images
#########################################

def getImages(arr):

    tmdb_id = arr[0]
    mediatype = arr[1]
    title = arr[2]
    plot = arr[3]
    poster = arr[4]

    if mediatype == 'movie':
        images_url = TMDB_MOVIES+tmdb_id+"/images"+TMDB_API_KEY
    else:
         images_url = TMDB_TVSHOWS+tmdb_id+"/images"+TMDB_API_KEY

    #Open and Read the Response
    request = Request(images_url)
    response_body = urlopen(request).read()
    response =  str(response_body)
    response = json.loads(response_body)
    results = response['backdrops']

    for image in results:
        preview = str(PREVIEW+image['file_path'])
        fanart = str(BACKDROP+image['file_path'])
        width = str(image['width'])
        height = str(image['height'])
        list_title = width + " x " + height + " :  " + title

        url = build_url({'mode': 'Wallpaper', 'image_url': fanart, 'title': title})
        li = list_item(list_title, DefaultIcon)
        li.setInfo(type='video', infoLabels={'mediatype': mediatype, 'title': title, 'plot': plot})
        li.setArt({'thumb': poster, 'icon': poster, 'poster': poster, 'fanart': fanart, 'landscape': fanart })
        addDir(url, li, False)

    endDir()

#########################################
# Build Index Menu                                                            
#########################################

#Mode
mode = args.get('mode', None)

#### Index ####
if mode is None:

    #TMDB Movies
    url = build_url({'mode': 'Index', 'foldername': 'Browse Movies'})
    li = list_item('Browse Movies', DefaultIcon)
    li.setArt({'thumb': DefaultIcon, 'icon': DefaultIcon, 'poster': DefaultIcon, 'fanart': DefaultFanart, 'landscape': DefaultFanart })
    addDir(url, li, True)

    #TMDB TV Shows
    url = build_url({'mode': 'Index', 'foldername': 'Browse TV Shows'})
    li = list_item('Browse TV Shows', DefaultIcon)
    li.setArt({'thumb': DefaultIcon, 'icon': DefaultIcon, 'poster': DefaultIcon, 'fanart': DefaultFanart, 'landscape': DefaultFanart })
    addDir(url, li, True)

    #TMDB Settings
    url = build_url({'mode': 'Index', 'foldername': 'Settings'})
    li = list_item('Settings', DefaultIcon)
    li.setArt({'thumb': DefaultIcon, 'icon': DefaultIcon, 'poster': DefaultIcon, 'fanart': DefaultFanart, 'landscape': DefaultFanart })
    addDir(url, li, False)

    endDir()

#########################################
# Build Index                                                        
#########################################

elif mode[0] == 'Index':
    foldername =args['foldername'][0]

    if foldername == 'Browse Movies':
        categories = ['Trending', 'Most Popular', 'Now Playing in Theatres', 'Upcoming', 'Most Rated', 'Companies', 'Genres', 'Years', 'Languages', 'Search ..']
        createMovieDir(categories)
        
    elif foldername == 'Browse TV Shows':
        categories = ['Trending', 'Most Popular', 'Currently on TV', 'Airing Today', 'Most Rated', 'Networks', 'Genres', 'Years', 'Languages', 'Search ..']
        createTVShowDir(categories)

    elif foldername == 'Settings':
        xbmcaddon.Addon(id='plugin.video.tmdbwalls').openSettings()
    
    endDir()

#########################################
# Build Movies Menu                                                       
#########################################

elif mode[0] == 'Movies':
    title = args['title'][0]

    #MOVIES
    if title == 'Trending':
        get_tmdb_info(TRENDING_MOVIES, 1)
    elif title == 'Most Popular':
        get_tmdb_info(POPULAR_MOVIES, 1)
    elif title == 'Now Playing in Theatres':
        get_tmdb_info(NOW_PLAYING_MOVIES, 1)
    elif title == 'Upcoming':
        get_tmdb_info(UPCOMING_MOVIES, 1)
    elif title == 'Most Rated':
        get_tmdb_info(TOP_RATED_MOVIES, 1)
    elif title == 'Companies':
        createSubDir(companies)
    elif title == 'Genres':
        createSubDir(movie_genres)
    elif title == 'Years':
        createSubDir(movie_years)
    elif title == 'Languages':
        createSubDir(movie_languages)
    elif title == 'Search ..':
        search_term = getSearchTerm()
        search_term =  urllib.quote_plus(search_term)
        get_tmdb_info(SEARCH_MOVIES+search_term, 1)
    
    endDir()

#########################################
# Build TV Shows Menu                                                      
#########################################

elif mode[0] == 'TV Shows':
    title = args['title'][0]
    
    #TV SHOWS
    if title == 'Trending':
        get_tmdb_info(TRENDING_TVSHOWS, 1)
    elif title == 'Most Popular':
        get_tmdb_info(POPULAR_TVSHOWS, 1)
    elif title == 'Currently on TV':
        get_tmdb_info(ON_THE_AIR_TVSHOWS, 1)
    elif title == 'Airing Today':
        get_tmdb_info(AIRING_TVSHOWS, 1)
    elif title == 'Most Rated':
        get_tmdb_info(TOP_RATED_TVSHOWS, 1)
    elif title == 'Networks':
        createSubDir(networks)
    elif title == 'Genres':
        createSubDir(tv_genres)
    elif title == 'Years':
        createSubDir(tv_years)
    elif title == 'Languages':
        createSubDir(tv_languages)
    elif title == 'Search ..':
        search_term = getSearchTerm()
        search_term =  urllib.quote_plus(search_term)
        get_tmdb_info(SEARCH_TVSHOWS+search_term, 1)
    
    endDir()

#########################################
# Build Sub Menus                                                         
#########################################

elif mode[0] == 'SubDir':
    title = args['title'][0]
    dir_url = args['dir_url'][0]
    dir_type = args['dir_type'][0]

    if dir_type == 'companies':
        get_tmdb_info(COMPANIES+dir_url, 1)
    elif dir_type == 'networks':
        get_tmdb_info(NETWORKS+dir_url, 1)
    elif dir_type == 'movie_genres':
        get_tmdb_info(MOVIE_GENRES+dir_url, 1)
    elif dir_type == 'tv_genres':
        get_tmdb_info(TV_GENRES+dir_url, 1)
    elif dir_type == 'movie_years':
        get_tmdb_info(MOVIE_YEARS+dir_url, 1)
    elif dir_type == 'tv_years':
        get_tmdb_info(TVSHOWS_YEARS+dir_url, 1)
    elif dir_type == 'movie_languages':
        get_tmdb_info(LANGUAGES_MOVIES+dir_url, 1)
    elif dir_type == 'tv_languages':
        get_tmdb_info(LANGUAGES_TVSHOWS+dir_url, 1)

    endDir()

#########################################
# Results                                              
#########################################

elif mode[0] == 'Result':
    tmdb_id = args['tmdb_id'][0]
    mediatype = args['mediatype'][0]
    title = args['title'][0]
    plot = args['plot'][0]
    poster = args['poster'][0]
    arr = [tmdb_id, mediatype, title, plot, poster]
    getImages(arr)


#########################################
# Download Image                                             
#########################################

elif mode[0] == 'Wallpaper':
    image_url = args['image_url'][0]
    title = args['title'][0]
    downloadWallpapers(title, image_url)
        
#########################################
# Next Page                                               
#########################################

elif mode[0] == 'Next Page':
    tmdb_url = args['tmdb_url'][0]
    page = args['page'][0]
    get_tmdb_info(tmdb_url, page)
