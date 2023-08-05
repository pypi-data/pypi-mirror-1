#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#      MPD WebAMP
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


import logging, cherrypy, turbogears, urllib, cgi, re, string, math, findlyrics
from turbogears import controllers, expose, validate, redirect, config
from mpd_webamp import json, mpdclient2
from os.path import *
import os

log = logging.getLogger("mpd_webamp.controllers")
        
        
def formatted_song(song):
    try:
        if (len(song.title) > 0):
            ttl = "<span class='title'>"+allsafe(song.title)+"</span>"
            try:
                art = "<span class='artist'>"+allsafe(song.artist)+"</span>"
            except:
                art = ""
            try:
                alb = "<span class='album'>("+allsafe(song.album)+")</span>"
            except:
                alb = ""
            mySong = ttl+art+alb
        else: mySong = ""
    except:
        mySong = ""
    
    try:
        if (len(mySong) > 0):
            return mySong
        else:
            if (song.file.find("/") > 0):
                S = song.file.split("/")
                s = S.pop()
                return u"<span class='title'>"+allsafe(s)+"</span>"
            else:
                return u"<span class='title'>"+allsafe(song.file)+"</span>"
    except:
        return "error"


def allsafe( s ):
    safe = cgi.escape(s).replace('"','&#34;').replace("'",'&#39;')
    try:
        safe = unicode(safe, 'utf-8')
    except TypeError:
        pass
    return safe


def minutes(val):
    if (val.isdigit()):
        val = int(val)
        d, h, m, s = fractSec(val)
        
        if (h > 0):
            hr = str(h)+":"
        else:
            hr = ""
        mn = str(m)+":"
        if (s < 10):
            sec = "0"+str(s)
        else:
            sec = str(s)
            
    else:
        mn = "0:"
        sec = "00"
        
    return hr+mn+sec

def fractSec(s):
    "Return days, hours, minutes, seconds given a value in seconds"
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return d, h, m, s

    
def tableStats(mpd):
    try:
        ms = mpd.stats()
        dy, hr, mn, sec = fractSec(int(ms.db_playtime))
        pt = str(dy)+" days, "+str(hr)+" hours, "+str(mn)+" minutes"
        st = string.Template("""<table>
                                    <th colspan="2" style="font-size:1.5em; font-weight:bold; align:center;padding-bottom:5px">Database Information</th>
                                    <tbody>
                                    <tr valign="top">
                                        <td align="right" width="50%"><b>Artists:</b>&nbsp;&nbsp;</td>
                                        <td width="50%">&nbsp;&nbsp;$artists</td>
                                    </tr>
                                    <tr valign="top">
                                        <td align="right" width="50%"><b>Albums:</b>&nbsp;&nbsp;</td>
                                        <td width="50%">&nbsp;&nbsp;$albums</td>
                                    </tr>
                                    <tr valign="top">
                                        <td align="right" width="50%"><b>Songs:</b>&nbsp;&nbsp;</td>
                                        <td width="50%">&nbsp;&nbsp;$songs</td>
                                    </tr>
                                    <tr valign="top">
                                        <td align="right" width="50%"><b>Total Playtime:</b>&nbsp;&nbsp;</td>
                                        <td width="50%">&nbsp;&nbsp;$play</td>
                                    </tr>
                                    </tbody>
                                </table>""")
        return st.safe_substitute(songs=ms.songs, artists=ms.artists, albums=ms.albums, play=pt)
    except:
        return "Error connecting to MPD!"


def createBrowselist(lsinfo):
    ua = cherrypy.request.headers.get('User-Agent', None)
    if (ua.find("Konqueror") > 0):
        rightclick = """onmousedown='return showBLmore(event, "${index}")'"""
    else:
        rightclick = """onmousedown='return false' oncontextmenu='return showBLmore(event, "${index}")'"""
            
    browse = "<table id='browselist_table'><tbody id='browselist_tablebody'>"
    rowTemp = string.Template(u"""
        <tr id='b${index}_tablerow' onclick='return BL_click(event, "${index}")' 
                                    onmouseover='BLover("b${index}_tablerow")'
                                    onmouseout='BLout("b${index}_tablerow")' """
                                    +rightclick+""">
            <td class='icon_$myClass'></td>
        """)
    
    i = 0
    for item in lsinfo:
        if (item.type == "directory"):
            d = item.directory.split("/")
            myId = item.directory
            myTxt = allsafe(d.pop())
            myClass = "folder"
            tmp = rowTemp.substitute(index=i, myClass=myClass)
        if (item.type == "file"):
            myId = item.file
            myTxt = formatted_song(item)
            myClass = "file"
            tmp = rowTemp.substitute(index=i, myClass=myClass)
        
        browse += tmp + u"<td id='"
        browse += allsafe(myId)
        browse += u"' class='"+myClass
        browse += "'>"+myTxt+u"""</td></tr><tr height="2px" width="100%"><td></td></tr>"""
        i = i + 1
    browse = browse + u"</tbody></table>"
    
    return browse


class Root(controllers.RootController):
    
    def __init__(self):
        controllers.RootController.__init__(self)
        self.host=config.get("mpd_host", "localhost")
        self.port=int(config.get("mpd_port", 6600))
        try:
            m = mpdclient2.connect(host=self.host, port=self.port)
            self.playlistInfo = m.playlistinfo()
            self.playlistID = m.status().playlist
        except:
            self.playlistInfo = []
            self.playlistID = -1
        
    
    def mpd(self):
        return mpdclient2.connect(host=self.host, port=self.port)
        
        
    @expose(template="mpd_webamp.templates.setup")
    def setup(self):
        kw_update = cherrypy.session.get("delay", 330)
        kw_stepIn = cherrypy.session.get("fadein", 300)
        kw_stepOut = cherrypy.session.get("fadeout", 400)
        kw_fps = cherrypy.session.get("fps", 40)
        kw_font = cherrypy.session.get("font", "normal")
        kw_theme = cherrypy.session.get("theme", "default")
        kw_updatesize = cherrypy.session.get("updatesize", 100)
        kw_listsize = cherrypy.session.get("listsize", 1000)
        
        return dict(update_int=kw_update, fadeIn=kw_stepIn, fadeOut=kw_stepOut, fps=kw_fps, font=kw_font, host=self.host, port=self.port, theme=kw_theme, upsize=kw_updatesize, listsize=kw_listsize)
    
    
    @expose(allow_json=True)
    def getThemes(self):
        themeList = ""
        t = os.listdir(join(dirname(__file__), "static/themes"))
        for item in t:
            if (item[0] != "."):
                if (item == cherrypy.session.get("theme", "default")):
                    s = " selected='selected'"
                else:
                    s = ""
                themeList += "<option id='opt_theme' value='"+item+"'"+s+">"+item+"</option>"
        return dict(themeList=themeList)
        
    @expose(allow_json=True)
    def testConn(self, host, port):
        try:
            m = mpdclient2.connect(host=host, port=int(port))
            s = tableStats(m)
        except:
            s = "<span style='color:red;font-size:1.5em; font-weight:bold; padding:20px'>Error Connecting to MPD!</span>"
        return dict(stats=s)
    
        
    @expose(template="mpd_webamp.templates.amp")
    def index(self, **kw):
        log.debug("MPD WebAMP is ready.")
        kw_update = kw.get("delay", cherrypy.session.get("delay", 330))
        kw_updatesize = kw.get("updatesize", cherrypy.session.get("updatesize", 100))
        kw_listsize = kw.get("listsize", cherrypy.session.get("listsize", 1000))
        kw_stepIn = kw.get("fadein", cherrypy.session.get("fadein", 300))
        kw_stepOut = kw.get("fadeout", cherrypy.session.get("fadeout", 400))
        kw_fps = kw.get("fps", cherrypy.session.get("fps", 40))
        kw_font = kw.get("font", cherrypy.session.get("font", "normal"))
        kw_theme = kw.get("theme", cherrypy.session.get("theme", "default"))
        kw_host = kw.get("host", cherrypy.session.get("host", self.host))
        kw_port = int(kw.get("port", cherrypy.session.get("port", self.port)))
        if (kw_host != self.host):
            cherrypy.session["browse"] = ""
            cherrypy.session["lyrics"] = ""
            cherrypy.session["search"] = ""
            cherrypy.session["dir"] = "/"
        self.host = kw_host
        self.port = kw_port
        cherrypy.session["delay"] = kw_update
        cherrypy.session["updatesize"] = kw_updatesize
        cherrypy.session["listsize"] = kw_listsize
        cherrypy.session["fadein"] = kw_stepIn
        cherrypy.session["fadeout"] = kw_stepOut
        cherrypy.session["fps"] = kw_fps
        cherrypy.session["theme"] = kw_theme
        cherrypy.session["font"] = kw_font
        cherrypy.session["host"] = self.host
        cherrypy.session["port"] = self.port
        try:
            m = self.mpd()
            last = cherrypy.session.get("last", "browse")
            # This value is actually used in seconds, not milliseconds
            kw_update = float(kw_update)/1000
            return dict(update_int=kw_update, fadeIn=kw_stepIn, fadeOut=kw_stepOut, fps=kw_fps, font=kw_font, last=last, theme=kw_theme)
        except:
            self.host = "Error connecting to mpd!"
            self.port = "Error connecting to mpd!"
            raise redirect("setup")


    @expose(allow_json=True)
    def browsempd(self, dir = "/"):
        cb = ""
        cd = ""
        d = ""
        back = ""
        if (dir == "[cache]"):
            cb = cherrypy.session.get("browse", "")
            dir = cherrypy.session.get("dir", "/")
        print dir
        
        if (dir != "/"):
            d = dir.split("/")
            cd = allsafe(d.pop())
        if (len(d) > 0):
            back = d.pop()
            if (back == cd):
                    back = ""

        if (cb == ""):
            m = self.mpd()
            lsinfo = m.lsinfo(dir.encode('utf-8')) 
            updb = ""
            if (dir == "/"):
                updb = u"""
                        <table>
                            <tr height="4px" width="100%"><td></td></tr>
                            <tr id='bupdb_tablerow' onclick='updateMPD()' 
                                        onmouseover='BLover("bupdb_tablerow")'
                                        onmouseout='BLout("bupdb_tablerow")'>
                                <td class='icon_updb'></td>
                                <td id='updb' class='folder'>Scan Music directory for new files</td>
                            </tr>
                            <tr height="4px" width="100%"><td></td></tr>
                        </table>
                    """
            browse = updb+createBrowselist(lsinfo)
        else:
            browse = cb
                    
        cherrypy.session["browse"] = browse
        cherrypy.session["dir"] = dir
        cherrypy.session["last"] = "browse"
        return dict(browselist=browse, back=back, current=cd, path=dir)
       

    @expose(allow_json=True)
    def browsePL(self):
        m = self.mpd()
        lsinfo = m.lsinfo("/")
        
        PL = """<table id='playlist_contents' onmousedown='return false'>"""
        rowTemp = string.Template("""
            <tr id='${myId}_tablerow'>
                <td  id='${myId}_left' class='icon_loadPL'></td>
                <td  id='$myId' class='$myClass' onclick='$click' onmouseover='loadPLover("$myId")' onmouseout='loadPLout("$myId")'>$Text</td>
                <td width="16px" onmouseover='remPLover("$myId")' onmouseout='remPLout("$myId")'><img id='${myId}_remove' class='icon_remove' onclick='loadJSONDoc("/removePL?name=$myId").addCallback(displayPL)'></td>
            </tr>
            <tr height="2px" width="100%"><td></td></tr>
            """)
        for item in lsinfo:
            if (item.type == "playlist"):
                myId = allsafe(item.playlist)
                myTxt = myId
                myClass = "PL_item"
                myClick = 'loadPlaylist("'+myId+'")'
                tmp = rowTemp.safe_substitute( myClass=myClass, myId=myId, Text=myTxt, click=myClick)
                PL += unicode(tmp)
        PL += "<tr id='cancel_tablerow'><td></td><td id='cancel' style='font-weight:bold' onmouseover='loadPLover(this.id)' onmouseout='loadPLout(this.id)' onclick='getPlaylist()'>Go back to Current Playlist</td><td></td></tr></table>"
        
        return dict(playlists=PL)


    @expose()
    def removePL(self, name):
        m = self.mpd()
        try:
            m.rm(name)
        except:
            pass
        
        raise redirect("/browsePL")


    @expose(allow_json=True)
    def playlist(self, **kw):
        m = self.mpd()
        list_start = int(kw.get("start", 0))
        list_size = int(cherrypy.session.get("updatesize", 200))
        max_size = int(cherrypy.session.get("listsize", 0))
        chunk = int(kw.get("chunk", 0))
        if (max_size > 0 and chunk < 1): chunk = 1
        head = ""
        foot = ""
        chunk_limit = max_size * chunk
        
        try:
            if (self.playlistID <> m.status().playlist):
                self.playlistInfo = m.playlistinfo()
                self.playlistID = m.status().playlist
        except:
            self.playlistInfo = m.playlistinfo()
            self.playlistID = m.status().playlist

        PL_count = len(self.playlistInfo)
        
        ua = cherrypy.request.headers.get('User-Agent', None)
        if (ua.find("Konqueror") > 0):
            rightclick = """onmousedown='return showPLmore(event, "${myId}")'"""
        else:
            rightclick = """onmousedown='return false' oncontextmenu='return showPLmore(event, "${myId}")'"""
        
        if (list_start <= PL_count):    
            if (list_start + list_size >= PL_count):
                list_end = PL_count
                more_PL = False
            else:
                list_end = list_start + list_size
                more_PL = True
        if (chunk_limit > 0):
            if (list_start < (chunk_limit-max_size)):list_start = chunk_limit-max_size
            if (list_start > chunk_limit):
                while (list_start >= chunk_limit):
                    log.debug("list_start="+str(list_start)+", chunk_limit="+str(chunk_limit)+". Next chunk.")
                    chunk += 1
                    chunk_limit = max_size * chunk
                list_start = chunk_limit - max_size
                
            if (chunk > 1 and list_start == chunk_limit - max_size):
                head = """
                    <tr id='h0_tablerow' class='PL_nav' onclick='getPlaylist("""+str(chunk_limit-max_size-max_size)+", "+str(chunk-1)+""")'
                        <td id='h0_left' class='icon_PL'>&nbsp;</td>
                        <td id='h0' class='TD_nav'>Get previous """+str(max_size)+""" songs</td>
                    </tr>
                    <tr height='1px'><td>&nbsp;</td></tr>
                    """
            if (PL_count > chunk_limit):
                if (list_end >= chunk_limit):
                    list_end = chunk_limit
                    more_PL = False
                    foot = """
                    <tr height='1px'><td>&nbsp;</td></tr>
                    <tr id='f0_tablerow' class='PL_nav' onclick='getPlaylist("""+str(list_end)+", "+str(chunk+1)+""")'
                        <td id='f0_left' class='icon_PL'>&nbsp;</td>
                        <td id='f0' class='TD_nav'>Get next """+str(max_size)+""" songs</td>
                    </tr>
                    """
        if (list_start <= PL_count):
            rowTemp = string.Template("""
                <tr id='${myId}_tablerow' onclick='$click' 
                                        onmouseover='PLover("$myId")' 
                                        onmouseout='PLout("$myId")' """
                                        +rightclick+""">
                    <td id='${myId}_left' class='icon_PL'>$myPosDisplay.</td>
                    <td id='$myId' class='$myClass'>$Text</td>
                </tr>
                <tr id='${myId}_spacer' height="2px" width="100%"><td></td></tr>
                """)

            PL = ""              
            for index in range(list_start, list_end):
                item = self.playlistInfo[index]
                myId = ("p" + str(item.pos))
                myTxt = formatted_song(item)
                myClass = "file"
                myClick = 'return PL_click(event, "'+str(item.pos)+'"); return false'
                tmp = rowTemp.safe_substitute(myPos=item.pos, myPosDisplay=int(item.pos)+1, myClass=myClass, myId=myId, Text=myTxt, click=myClick)
                PL += unicode(tmp)
            PL = head+PL+foot
            return dict(playlist=PL, more_start=list_end, more=more_PL, playlist_version=self.playlistID, length=PL_count, chunk=chunk, start=list_start)


    @expose(allow_json=True)
    def playlist_changes(self, version, len_old, changes_from="0", **kw):
        ua = cherrypy.request.headers.get('User-Agent', None).lower()
        ls = int(cherrypy.session.get("listsize", 0))
        rem = 0
        add = ""
        change = dict()
        changeHTML = dict()
        i=0
        len_new = -1
        changes_from = int(changes_from)
        changes_to = 0
        more_changes = False
        version = int(version)
        len_old = int(len_old)
        kw_chunk = int(kw.get("chunk",0))
        chunk_start = 0
        chunk_end = 0
        if (kw_chunk > 0 and ls > 0):
            chunk_start = (ls * kw_chunk) - ls
            chunk_end = chunk_start + ls
        
        if (ua.find("gecko") == 0 or ua.find("like gecko") > 0):
            raise redirect("playlist")
        
        if (changes_from == 0):
            m = self.mpd()
            self.playlistInfo = m.playlistinfo()
            try:
                self.playlistID = m.status().playlist
            except:
                self.playlistID = -1
            
            len_new = int(m.status().playlistlength)
            if (len_new >= chunk_end):
                args = "?start=0"+str(chunk_end)+"&chunk=1"
                if (len_new > 0 and ls > 0):
                    if ((float(len_new)/float(ls)) > 1):
                        args = "?start="+str(len_new)+"&chunk=1"
                
                raise redirect("playlist"+args)
            if (len_old >= chunk_end and len_new <= chunk_end):
                raise redirect("playlist?start="+str(chunk_start)+"&chunk="+str(kw_chunk))
            
            
            if (len_old < 1):
                raise redirect("playlist")
            e = len_new
            if (chunk_end > 0 and chunk_end < len_new): e = chunk_end
            if (e > len_old):
                ua = cherrypy.request.headers.get('User-Agent', None)
                if (ua.find("Konqueror") > 0):
                    rightclick = """onmousedown='return showPLmore(event, "p${myId}")'"""
                else:
                    rightclick = """onmousedown='return false' oncontextmenu='return showPLmore(event, "p${myId}")'"""
                
                rowTemp = string.Template(u"""
                    <tr id='p${myId}_tablerow' onclick='return PL_click(event, "${myId}"); return false' 
                                            onmouseover='PLover("p${myId}")' 
                                            onmouseout='PLout("p${myId}")' 
                                            """+rightclick+""">
                    </tr>
                    <tr id='p${myId}_spacer' height="2px" width="100%"><td></td></tr>
                    """)
    
                PL = ""
                for index in range(len_old, e):
                    item = self.playlistInfo[index]
                    myId = str(item.pos)
                    PL += rowTemp.substitute(myId=myId)
                add = PL
    
            else:
                rem = len_old - e
            m = self.mpd()
            plc = m.plchanges(version)
            n = []
            for item in plc:
                ip = int(item.pos)
                if (ip >= chunk_start and ip <= e):
                    n.append(item.pos)
            self.playlistInfo = m.playlistinfo()
            if (len_new == len(n)):
                raise redirect("playlist")
            else:
                cherrypy.session["plchanges"] = n
            
        else:
            n = cherrypy.session.get("plchanges", [])
                
        cc = len(n)
        if (cc == 0):
            more_changes = False
            i = 0
        else:
            if (changes_from == 0): list_size = 1
            else: list_size = int(cherrypy.session.get("updatesize", 100))
            if (changes_from <= cc):    
                if (changes_from + list_size > cc):
                    changes_to = cc
                    more_changes = False
                else:
                    changes_to = changes_from + list_size
                    more_changes = cc-changes_to
                for index in range(changes_from, changes_to):
                    item = self.playlistInfo[int(n[index])]
                    p = item.pos
                    li = str(int(p) + 1)
                    row = u"<td id='p"+p+"_left' class='icon_PL'>"+li+u".</td><td id='p"+p+u"' class='file'>"+formatted_song(item)+u"</td>"
                    change[i] = "p"+p+"_tablerow"
                    changeHTML[i] = row
                    i = i+1
                #i -= 1
            
        if not more_changes: cherrypy.session["plchanges"] = ""
            
        ret = dict(remove=rem, add=add, change=change, changeHTML=changeHTML, change_count=i, version=self.playlistID, old_version=version, length=len_new, len_old=len_old, changes_to=changes_to, changes_from=changes_from, more_changes=more_changes)
        log.debug(str(i)+" changes sent, changes left = "+str(cc-changes_to))
        return ret

    
    @expose(allow_json=True)
    def addplay(self, song = "", more = False, play = False):
        m = self.mpd()
        p = len(m.playlistinfo())
        m.add(song.encode('utf-8'))
        if (play == "True"):
            m.play(p)
        if (more == "True"):
            return dict(pID=p)
        else:
            return dict(OK="OK")


    @expose(allow_json=True)
    def save(self, name):
        m = self.mpd()
        m.save(name.encode('utf-8'))
        log.debug("playlist saved as "+name)
        raise redirect("/playlist")


    @expose(allow_json=True)
    def load(self, playlist):
        m = self.mpd()
        m.load(playlist.encode('utf-8'))
        raise redirect("/playlist")


    @expose()
    def set(self, action):
        m = self.mpd()
        if (action == "normal"):
            m.random(0)
        elif (action == "random"):
            m.random(1)
        elif (action == "shuffle"):
            m.shuffle()
        
        return dict(OK="OK")


    @expose()
    def control(self, action):
        m = self.mpd()
        if (action=="play"):    
            m.play()

        elif (action=="stop"):
            m.stop()

        elif (action=="next"):
            m.next()

        elif (action=="prev"):
            m.previous()

        elif (action=="pause"):
            m.pause(True)

        else:
            log.debug(action)
            
        m.clearerror()
        
        return dict(OK="OK")
        


    @expose()
    def playnow(self, myid):
        m = self.mpd()
        m.play(int(myid))
        m.clearerror()
        return dict(ok="OK")
        


    @expose()
    def remove(self, myid):
        m = self.mpd()
        m.delete(int(myid))
        return dict(ok="OK")


    @expose()
    def move(self, fromid, toid):
        m = self.mpd()
        m.move(int(fromid),int(toid))
        return dict(ok="OK")


    @expose(allow_json=True)
    def status(self, **kw):
        kw_song = kw.get("songid", "")
        kw_time = kw.get("time", "")
        m = self.mpd()
        s = m.status()
        try:
            self.playlistID = s.playlist
        except:
            pass
        
        try:
            u = s.updating_db
            log.debug("updating Database " + u)
            cherrypy.session["search"] = ""
            cherrypy.session["browse"] = ""
        except:
            u = False
            
        # If one attribute is missing, better to just drop the whole thing.  A few dropped
        # status updates won't be noticed.
        try:
            v = s.volume
            mystate = "?"
            c = False
            P = False
            t = False
            prettyTime = False
            prettySong = False
            songPrefix = ""
    
            mystate = s.state
            if (s.state == "stop"):
                mystate = "Stopped"
                cherrypy.session["lyrics"] = ""
            elif (s.state == "pause"):
                mystate = "Paused"
                songPrefix = "<span class='pos'>Paused:</span>"
            elif (s.state == "play"):
                mystate = "Playing"
            
            if (u == False):
                if (mystate != "Stopped"):
                    t = s.time
                    P = s.song
                    if (t != kw_time):
                        T = t.split(":")
                        elapsed = str(T[0])
                        total = str(T[1])
                        prettyTime = minutes(elapsed) + " / " + minutes(total)
                    if (P != kw_song):
                        cherrypy.session["lyrics"] = ""
                        p = m.playlistinfo()
                        c = p[int(P)]
                        pos = str(int(c.pos)+1)
                        prettySong = songPrefix + "<span class='pos'>"+pos+".</span>" + formatted_song(c)
            
            ret = dict(state=mystate, volume=v, time=t, prettyTime=prettyTime, PLpos=P, cur_song=prettySong, updating = u, playlist_version=s.playlist)
      
        except:
            log.debug("Error retrieving status from mpd")
            ret = dict(Error="error")
        
        return ret


    @expose()
    def setvol(self, vol):
        m = self.mpd()
        if (vol == "up"):
            s = m.status()
            v = int(s.volume) + 5
        elif (vol == "down"):
            s = m.status()
            v = int(s.volume) - 5
        else:
            v = int(vol)
        if (v < 0):
            v = 0
        if (v > 100):
            v = 100
        m.setvol(v)

        return dict(vol=v)
        

    @expose()
    def seek(self, seek_to):
        m = self.mpd()
        try:
            m = self.mpd()
            s = m.status()
            t = s.time.split(":")
            pos = t[0]
            new_pos =  int(pos)+int(seek_to)
            m.seek(int(s.song), new_pos)
        except:
            new_pos = "Error"
        return dict(pos=new_pos)


    @expose()
    def clearPlaylist(self):
        m = self.mpd()
        m.clear()
        raise redirect("/playlist")


    @expose()
    def updateMPD(self):
        m = self.mpd()
        m.update()
        log.debug("Updating Database")
        return "OK"
        
        

    @expose(allow_json=True)
    def nowplaying(self, **kw):
        np = ""
        kw_link = kw.get("link", False)
        if (kw_link):
            if (kw_link == "redo"):
                cherrypy.session["lyrics"] = ""
            else:
                altL = findlyrics.parse(kw_link).lyrics
                onp = cherrypy.session.get("lyrics","")
                ls = onp.find("<div id='lyrics'")
                le = onp.find("</div>", ls)+6
                np = onp[:ls] + altL + onp[le:]
        if (np == ""):
            cl = cherrypy.session.get("lyrics", "")
            if (cl == ""):
                m = self.mpd()
                s = m.status()
                
                if (s.state != "stop"):
                    p = m.playlistinfo()
                    cur_song = p[int(s.song)]
                    f = findlyrics.Song(cur_song)
                    f.search()
                    np = f.SearchResults.parse(0).table
                    rc = f.SearchResults.count
                    if (rc > 1):
                        alt = "<br><div style='padding:10px'><b>Full Lyrics Search Results:</b><br><br>"
                        for i in range(0, rc-1):
                            alt += "<a href='javascript:getNowPlaying(\""+f.SearchResults.links[i]+"\")'>"
                            alt += f.SearchResults.labels[i]+"</a><br>"
                        alt += "</div>"
                        np += alt
                    np += "<div style='padding:10px;color:#555'>Lyrics by Findlyrics.com, Similar Artists by last.fm, album art courtesy of amazon.com using MusicBrainz.com metadata.</div>"
                else:
                    stats = tableStats(m)
                    np = "<br/><center>No song playing...</center><br/><br/>"+stats
            else:
                np = cl
            
        cherrypy.session["lyrics"] = np
        cherrypy.session["last"] = "lyrics"
        
        return dict(info=np)
    
    
    @expose(allow_json=True)
    def getSearch(self, search_for, search_what):
        if (search_for == "[cache]"):
            search_for = cherrypy.session.get("search_for", "")
            search_what = cherrypy.session.get("search_what", "filename")
            cs = cherrypy.session.get("search", "")
        else:
            cs = ""
        
        sb = """
            <div id="searchbox">
                <select id="select_what" name="what" class="search">
                    <option id="opt_artist" value="artist">Artist</option>
                    <option id="opt_album" value="album">Album</option>
                    <option id="opt_title" value="title">Title</option>
                    <option id="opt_filename" value="filename">File Name</option>
                </select>
                <input id="searchterm" type="text" class="search" onfocus="inputfocus=true" onblur="inputfocus=false" onkeydown='fullSearch(this.value, event)' value='"""+search_for+"""'/>
                <input id="searchButton" type="button" onclick="getSearch($('select_what').value,$('searchterm').value)" value="Search" class="search"/>
            </div>
            """
        #set the last Search What option to selected, first verify that it is valid to avoid mangled html
        v = "artist album title filename"
        if (v.find(search_what) > 0):
            sb = sb.replace("_"+search_what, "_"+search_what+'" selected="selected')
       
        if (len(search_for) > 0):
            if (len(cs) > 0):
                result = cs
            else:
                m = self.mpd()
                s = m.search(search_what, search_for)
                if (len(s) > 0):
                    result = sb+createBrowselist(s)
                else:
                    result = sb+"<br><center>No results found...</center>"
        else:
            result = sb
            
        cherrypy.session["search"] = result
        cherrypy.session["search_for"] = search_for
        cherrypy.session["search_what"] = search_what
        cherrypy.session["last"] = "search"
        return dict(result=result, search_what=search_what, search_for=search_for)
        