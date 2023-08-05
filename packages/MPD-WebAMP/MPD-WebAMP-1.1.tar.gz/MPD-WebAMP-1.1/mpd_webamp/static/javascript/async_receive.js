function delayPlaylistFetch(pv) {
    if (isInteger(playlist_version)) {old_pv = parseInt(playlist_version)}
    else {old_pv = -1}
    if (old_pv >= 0 && pv != playlist_version) {getPlaylistChanges()}
}

function displayStatus(result) { 
    if (result["Error"]) {

    }
    else {
        var ui = update_interval
        var csi = -1
        var pv = -1
        var old_pv = -1
        if (isInteger(result["PLpos"])) {csi = parseInt(result["PLpos"])}
        if (playlist_changing == false){
            if (isInteger(result["playlist_version"])) {pv = parseInt(result["playlist_version"])}
            if (isInteger(playlist_version)) {old_pv = parseInt(playlist_version)}
            if (pv >= 0 && old_pv >= 0) {
                if (pv != old_pv) {
                    // This will only be called if another client is changing the playlist
                    // wait for them to stop or pause for 2 seconds before loading changes
                    callLater(2, delayPlaylistFetch, pv)
                }
            }
        }

        if (result["state"] == "Playing") {
            $("play").style.height = "0px"
            $("pause").style.height = "32px"
        }
        else {
            $("play").style.height = "32px"
            $("pause").style.height = "0px"
            ui = ui * 10
        }
        if (result["state"] == "Stopped") {
            swapElementClass("song", "song_small", "song_big")
            $("song").innerHTML = "Stopped"
            $("time").innerHTML = "0:00 / 0:00"
            current_song_id = null
        }
    
        if (result["volume"]) {$("vol-front").style.width = ((result["volume"]/2)+5)+"px"}
        
        if (result["prettyTime"]) {
            if ( result["prettyTime"].length > 11) { swapElementClass("time", "song_big", "song_small") }
            else { swapElementClass("time", "song_small", "song_big") }
            current_play_time = result["time"]
            $("time").innerHTML = result["prettyTime"]
        }
                
        if (result["cur_song"]) {
            $("song_calc").innerHTML = result["cur_song"]
            var sd = elementDimensions("song_calc")
            var available = elementDimensions("song-details")["w"]-137
            if (sd["w"] > available) {swapElementClass("song", "song_big", "song_small")}
            else {swapElementClass("song", "song_small", "song_big")}
            
            $("song").innerHTML = result["cur_song"]
            if (active_switch == "showNowPlaying" && current_song_id != csi && current_song_id != "init") {getNowPlaying()}
            if (current_song_id != csi) {
                try {removeElementClass("p"+current_song_id+"_tablerow", "playing")}
                catch (err) {}
                current_song_id = csi
                gotoCurrentSong()
                }
        }

        if (result["updating"]) {
            $("song").innerHTML = "Updating Database..."
            current_song_id = ""
            }
        else {
            if (updb_called) {
                updb_called = false
                if (active_switch == "showBrowse") {getBrowse("[cache]")}
            }
        }
        
        if (!playlistLoading) {
            callLater(ui, getStatus)
        }
    }
}

function displayBrowse(result) {
    removeBorder('BL');
    select_start = -1
    select_end = -1
    
    cd = result["current"]
    $("crumbtrail").innerHTML = cd
    updateNodeAttributes("addAll", {"onclick":"addPlay('"+escape(result["path"])+"')", "style": {"width": "37px"}});
    if (result["back"] == "") {
        updateNodeAttributes("crumbtrail", {"style": {"left": "38px"}})
        updateNodeAttributes("back", {"style": {"width": "0px"}, "onclick": ""})
    }
    else {
        updateNodeAttributes("crumbtrail", {"style": {"left": "56px"}})
        updateNodeAttributes("back", {"style": {"width": "24px"}, "onclick": "getBrowse('"+escape(result["back"])+"')"})
    }
    var dim = elementDimensions("crumbtrail")
    if (dim["h"] > 28) {
        updateNodeAttributes("centerLeft", {"style": {"top": "72px"}})
        $("centerLeftHead").style.height = "48px"
    }
    else {
        updateNodeAttributes("centerLeft", {"style": {"top": "52px"}})
        $("centerLeftHead").style.height = "28px"
    }
    setOpacity("centerLeft", 0.01)
    $("browselist").innerHTML = result["browselist"]
    stepOpacity("centerLeft", 0.01, 1, step_in_duration)
    
}


function displayNowPlaying (result) {
    removeBorder('BL')
    updateNodeAttributes("centerLeft", {"style": {"top": "52px"}})
    $("centerLeftHead").style.height = "28px"
    updateNodeAttributes("back", {"style": {"width": "0px"}, "onclick": ""})
    updateNodeAttributes("addAll", {"onclick":"", "style": {"width": "0px"}});
    replaceChildNodes("crumbtrail", "Now Playing")
    setOpacity("centerLeft", 0.01)
    $("browselist").innerHTML = result["info"]
    stepOpacity("centerLeft", 0.01, 1, step_in_duration)
}


function displaySearch (result) {
    removeBorder('BL')
    updateNodeAttributes("centerLeft", {"style": {"top": "52px"}})
    $("centerLeftHead").style.height = "28px"
    updateNodeAttributes("back", {"style": {"width": "0px"}, "onclick": ""})
    updateNodeAttributes("addAll", {"onclick":"addAllSR()", "style": {"width": "37px"}});
    if (result["search_for"] == "") {l = "Search"}
    else {l = "Search Results for '"+result["search_for"]+"'"}
    replaceChildNodes("crumbtrail", l)
    setOpacity("centerLeft", 0.01)
    $("browselist").innerHTML = result["result"]
    stepOpacity("centerLeft", 0.01, 1, step_in_duration)
}


function displayPlaylist(result) {
    if (typeof(result["playlist"]) == "undefined") {
        displayPlaylistChanges(result)
    }
    else {
        if (!playlistLoading) {
            select_start = -1
            select_end = -1
            PL_action = ""
            playlist = ""
            removeBorder('PL')
            $("choosePlaylist").style.height = "0px"
            $("currentPlaylist").style.height = "28px"
        }
        
        if (result["more"]) {
            status_break = true
            $("playlist").innerHTML = "<br><center>Loading Playlist... " + result["more_start"] + " songs</center>"
            playlist = playlist + result["playlist"]
            playlistLoading = true
            callLater(0.01, getPlaylist, result["more_start"], result["chunk"])
            pv = parseInt(result["playlist_version"])
            if (pv != -1) {playlist_version = pv}
        }
        else {
            var sizer = ""
            playlist_length = result["length"]
            if(playlist_length < 10000){w = 42}
            if(playlist_length < 1000){w = 32}
            if(playlist_length < 100){w = 22}
            if(playlist_length < 10){w = 12}
            if(playlist_length>0){
                sizer = "<tr><td id='sizer' width='"+w+"px'>&nbsp;</td><td>&nbsp;</td></tr>"
            }
            var render = function () {
                            $("playlist").innerHTML = "<table id='playlist_contents' style='table-layout:fixed'>"+sizer+playlist+result["playlist"]+"</table>"
                            playlist_version = parseInt(result["playlist_version"])
                            if (parseInt(result["chunk"])>0) {
                                chunk = result["chunk"]
                                chunk_start = result["start"]
                            }
                            else {chunk=0}
                            playlistLoading = false
                            playlist_changing = false
                            $("plLabel").innerHTML = "Playlist"
                            status_break = false
                            getStatus()
                        }
            if (parseInt(result["more_start"]) > 1000) {
                $("playlist").innerHTML = "<br><center>Loading Playlist... " + result["more_start"] + " songs</center><br><center>Please Wait</center>"
                callLater(0, render)
            }
            else {render()}
        }
    }
}


function displayPlaylistChanges(result) {
    if (typeof(result["playlist"]) != "undefined") {displayPlaylist(result)}
    else {
        status_break = true
        playlist_version = result["version"]
        l = parseInt(result["length"])
        r = parseInt(result["remove"])
        a = result["add"]

        if (r > 0) {
            t = $("p"+l+"_tablerow").parentNode
            for (i=l;i<(l+r);i++) {
                t.removeChild($("p"+i+"_tablerow"))
                t.removeChild($("p"+i+"_spacer"))
            }
        }
        if (a.length > 0) {
            if(l < 10000){w = 42}
            if(l < 1000){w = 32}
            if(l < 100){w = 22}
            if(l < 10){w = 12}
            $("sizer").style.width = w+"px"
            t = $("playlist_contents")
            tH = t.innerHTML
            t.innerHTML = tH.replace("</tbody>", a+"</tbody>")
        }
        if(l>=0) {playlist_length = l}
        callLater(0, displayChanges, result)
    }
}

function displayChanges(result) {
    c = result["change"]
    cc = parseInt(result["change_count"])
    cH = result["changeHTML"]
    if (cc > 0){
        for (i=0;i<cc;i++) {
            $(c[i]).innerHTML = cH[i]
        }
    }
    if (result["more_changes"]) {
        var prc = 10 - Math.floor(((parseInt(result["more_changes"])/playlist_length))*10)
        var prg = "Updating Playlist..."
        var dv = "<span style='color:gray'>"
        switch (prc) {
            case 0: prg = dv+"||||||||||</span>";break
            case 1: prg = "|"+dv+"|||||||||</span>";break
            case 2: prg = "||"+dv+"||||||||</span>";break
            case 3: prg = "|||"+dv+"|||||||</span>";break
            case 4: prg = "||||"+dv+"||||||</span>";break
            case 5: prg = "|||||"+dv+"|||||</span>";break
            case 6: prg = "||||||"+dv+"||||</span>";break
            case 7: prg = "|||||||"+dv+"|||</span>";break
            case 8: prg = "||||||||"+dv+"||</span>";break
            case 9: prg = "|||||||||"+dv+"|</span>";break
            case 10: prg = "||||||||||";break
        }
        $("plLabel").innerHTML = prg
        i = parseInt(result["changes_to"])
        var args = "?version="+result["old_version"]+"&len_old="+result["len_old"]+"&changes_from="+i+"&chunk="+chunk
        var cb = function (args, result){
            displayStatus(result)
            PLd = loadJSONDoc("playlist_changes"+args)
            PLd.addCallback(displayChanges)
        }
        var cbb = bind(cb, self, args)
        status_last_request++
        loadJSONDoc("status?songid="+current_song_id+"&time="+current_play_time).addCallback(cbb)
    }
    else {
        playlist_changing = false
        status_break = false
        getStatus()
        $("plLabel").innerHTML = "Playlist"
    }
}


function displayPL(result) {
    $("currentPlaylist").style.height = "0px"
    $("choosePlaylist").style.height = "28px"
    $("playlist").innerHTML = result["playlists"]
}
