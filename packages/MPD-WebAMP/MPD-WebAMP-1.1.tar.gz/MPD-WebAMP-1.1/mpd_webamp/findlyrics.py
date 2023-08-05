#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#      findlyrics.py
#
#      Copyright 2007 Chris Seickel <cseickel@gmail.com>
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#
###############################################################################
###############################################################################

import string, urllib, datetime
from types import *


class ParseResults:
    "Container for Parsed Results"
    
    def __init__(self):
        self.table = ""
        self.lyrics = ""
        self.image = ""
        self.similar = ""



class SearchResults:
    "Container for Search Results"
    
    def __init__(self):
        self.count = 0
        self.links = []
        self.labels = []
        self.similarXML = ""
        self.albumXML = ""
        
    def parse(self, result = 0):
        try:
            link = self.links[result]
        except:
            link = ""
        return parse(link, self.albumXML, self.similarXML)



class Song:
    
    def __init__(self, song = ""):
        self.artist = ""
        self.album = ""
        self.title = ""
        self.SearchResults = SearchResults()
        if (len(song) > 0): self.load(song)
        
        
    def load(self, song):
        artist = ""
        album = ""
        title = ""
        
        if (type(song) is StringType):
            myfileFull = song.split("/")
        else:
            if (song.has_key("album")):
                album = song["album"]
            if (song.has_key("artist")):
                artist = song["artist"]
            if (song.has_key("title")):
                title = song["title"]
            if (song.has_key("file")):
                myfileFull = song["file"].split("/")

        # If we only have the file name, parse it for artist and title
        if (title == ""):
            myfile = myfileFull.pop()
            myfile = myfile[:-4]
            s = myfile.find("(")
            if (s > 0):
                e = myfile.rfind(")")
                if (e < 0):
                    e = s
                myfile = myfile[:s-1] + myfile[e+1:]
            s = myfile.split("-")
            if (len(s) > 0):
                title = s.pop().strip()
                artist = s[0].strip()
                if (artist.isdigit()):
                    artist = ""
                    if (len(s) > 1):
                        artist = s[1]
            else:
                title = myfile
        self.artist = artist
        self.album = album
        self.title = title


    def search(self):
        artist = _clean(self.artist)
        album = _clean(self.album)
        title = _clean(self.title)
        year = str(datetime.date.today().year)
        
        #Get similar artists XML file from last.fm
        try:
            search_url = "http://ws.audioscrobbler.com/1.0/artist/"+artist+"/similar.xml"
            conn = urllib.urlopen(search_url)
            data = conn.read()
            conn.close()
            self.SearchResults.similarXML = "<lastfmurl>http://www.last.fm/music/"+artist+"</lastfmurl>"+data
        except:
            self.SearchResults.similarXML = ""
            
        #Grab album metadata from musicbrainz.com
        try:
            search_url = "http://musicbrainz.org/ws/1/release/?type=xml&artist="+artist+"&title="+album+"&limit=1"
            conn = urllib.urlopen(search_url)
            data = conn.read()
            conn.close()
            self.SearchResults.albumXML = data
        except:
            self.SearchResults.albumXML = ""
        
        # Findlyrics.com search
        if (len(title) > 0):
            search = "http://www.findlyrics.com/search/?as_q=1&artist=$artist&artist_match=0&song=$title&song_match=0&album=$album&album_match=1&from_year=1900&to_year="+year+"&lyrics%5B1%5D=&lyrics_match%5B1%5D=1&lyrics%5B2%5D=&lyrics_match%5B2%5D=1&lyrics%5B3%5D=&lyrics_match%5B3%5D=1"
            search_temp = string.Template(search)
            search_url = search_temp.safe_substitute(artist=artist, title=title, album = album)
            
            conn = urllib.urlopen(search_url)
            data = conn.read()
            conn.close()
            
            #If the first search doesn't get any results, drop the album
            if (data.find("Your search did not match any lyrics.") > 0 and len(album) > 0):
                search_url = search_temp.safe_substitute(artist=artist, title=title, album = "")
                conn = urllib.urlopen(search_url)
                data = conn.read()
                conn.close()
            #If still no results, specify closest matach instead of exact match
            if (data.find("Your search did not match any lyrics.") > 0):
                search_url = string.replace(search_url, "_match=0", "_match=1")
                conn = urllib.urlopen(search_url)
                data = conn.read()
                conn.close()
                
            #If we found results, parse the links and save them
            if (data.find("Your search did not match any lyrics.") < 0):
                s = data.find("<h1>Advanced Search Results</h1>")
                e = data.find("<div", s)
                data = data[s:e]
                
                links = []
                labels = []
                s = 1
                e = 1
                while (s > 0 and e > 0):
                    s = data.find("<a href=") + 9
                    e = data.find('">', s) - 1
                    if (s > 0 and e > 0):
                        links.append("http://www.findlyrics.com"+data[s:e]+"/?print")
                        s = data.find(">", e) + 1
                        e = data.find("</a>", s)
                        if (s > 0 and e > 0):
                            labels.append(data[s:e])
                            data = data[e:]
                            
                self.SearchResults.links = links
                self.SearchResults.labels = labels
                self.SearchResults.count = len(links)
                
        
    def quickSearch(self):
        self.search()
        return self.SearchResults.parse()



#make URL safe for insertion into findlyrics.com search url
def _clean(item):
    s = item.find("(")
    if (s > 0):
        e = item.rfind(")")
        if (e < 0):
            e = s
        item = item[:s-1] + item[e+1:]
    item = string.replace(item, "&","and")
    item = string.replace(item, "!","")
    item = string.replace(item, "?","")
    item = string.replace(item, ".","")
    item = string.replace(item, ":","")
    item = string.replace(item, ";","")
    item = string.replace(item, "'","")
    item = string.replace(item, '"',"")
    item = string.replace(item, ","," ")
    item = string.replace(item, " - "," ")
    item = string.replace(item, "-"," ")
    item = urllib.quote_plus(item)
    return item


def _parseSimilar(xml):
    s = 1
    e = 1
    h = ""
    s = xml.find("<lastfmurl>") + 11
    if (s > 0):
        e = xml.find("</lastfmurl>")
        if (e > 0):
            u = "<span style='font-size:2em;font-weight:bold'><a href='"+xml[s:e]+"' target='_blank'>"
            s = xml.find('<similarartists artist="') + 24
            if (s > 0):
                e = xml.find('"', s)
                if (e > 0):
                    h = u+xml[s:e]+"</a></span><br/><br/>"
                    
    i = 0
    h += "<span style='font-size:1.5em;font-weight:bold'>Top 10 Similar Artists</span>"
    while (s > 0 and e > 0 and i < 10):
        s = xml.find("<artist>")
        name = ""
        url = ""
        match = ""
        if (s > 0):
            e = xml.find("</artist>") + 9
            data = xml[s:e]
            xml = xml[e:]
            s = data.find("<name>") + 6
            e = data.find('</name>', s)
            if (s > 0 and e > 0):
                name = data[s:e]
            s = data.find("<url>") + 5
            e = data.find("</url>", s)
            if (s > 0 and e > 0):
                url = data[s:e]
            s = data.find("<match>") + 7
            e = data.find("</match>", s)
            if (s > 0 and e > 0):
                if (len(data[s:e]) > 0):
                    match = "&nbsp;&nbsp;<i>(score: "+data[s:e]+")</i>"
            if (len(name) > 0 and len(url) > 0):
                h += "<div class='similar'><a href='"+url+"' target='_blank'>"+name+"</a>"+match+"<br></div>"
                i += 1
    return h

#If amazon doesn't have the 240x240, they return a blank image, so check the file size
def _getValidImage(asin):
    base = "http://images.amazon.com/images/P/"+asin
    f = urllib.urlopen(base+".01._AA240_SCLZZZZZZZ_.jpg")
    s = len(f.read())
    if(s > 1000): return base+".01._AA240_SCLZZZZZZZ_.jpg"
    else:
        f = urllib.urlopen(base+".01.MZZZZZZZ.jpg")
        s = len(f.read())
        if(s > 1000): return base+".01.MZZZZZZZ.jpg"
        else: return ""
        


def parse(lyrics="", album="", similar=""):
    """parse(lyrics, album, similar)
    Parse print view lyrics page from findlyrics.com and return a ParseResults object.
    lyrics should be a findlyrics.com url, album should be musicbrainz release xml, similar
    should be audioscrobbler's similar.xml"""
    
    pr = ParseResults()
    
    if (similar != ""): pr.similar = _parseSimilar(similar)
    else: pr.similar = ""
    
    asin = ""
    if (album != ""):
        s = album.find("<asin>") + 6
        if (s > 6):
            e = album.find("</asin>", s)
            if (e > 0): asin = album[s:e]
    if (len(asin) == 10):
        pr.image = _getValidImage(asin)
    if (len(pr.image) == 0):
        s = similar.find("picture=") + 9
        if (s > 8):
            e = similar.find('"', s)
            if (e > 0):
                pr.image = similar[s:e]
    
    if (len(lyrics) > 0):
        conn = urllib.urlopen(lyrics)
        data = conn.read()
        conn.close
        #Grab the lyrics cell
        s = data.find('<td width="70%">') + 16
        e = data.find("</td>", s) + 8
        data = data[s:e] 
        #Step through all the links and remove the ads from the lyrics
        i = 0
        while (data.find("<a", i) > 0):
            start_a = data.find("<a", i)
            end_a = data.find("</a>", start_a) + 4
            if (data.find("Music Download", start_a, end_a) > 0):
                data = data[:start_a-1] + data[end_a+1:].lstrip("<br>")
                data.lstrip
            i = end_a
        #All the links are relative, we need to insert the full path to avoid broken links
        pr.lyrics = string.replace(data, '<a href="/', '<a target="_blank" href="http://www.findlyrics.com/')
    #Offer a Submit Lyrics button if no lyrics found.
    if (len(pr.lyrics)==0):
        pr.lyrics = """<br><br><center>No lyrics found for this song.</center><br><br><center><a href="http://www.findlyrics.com/submit_song/" target="_blank"><img alt="submit lyrics" src="http://www.findlyrics.com/img/submit.gif" width="176" height="28" border="0" /></a></center>"""
    
    pr.image = "<div id='album' class='art'><center><img src='"+pr.image+"'></center></div>"
    pr.lyrics = "<div id='lyrics'>"+unicode(pr.lyrics, 'utf-8')+"</div>"
    pr.similar = "<div id='SimlarArtists'>"+unicode(pr.similar, 'utf-8')+"</div>"
    pr.table = "<table><tr><td width='240px'><br/>"+pr.image+pr.similar
    pr.table += "<td width='15px'>&nbsp;</td></td><td>"+pr.lyrics+"</td></tr></table>"
    
    return pr
