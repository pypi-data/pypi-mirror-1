// orderedRequests() is used when commands need to be given to mpd in a specific
// order.  The nature of asynchronous requests is that you can not garauntee in
// what order they will be received and processed.
// It expects an Array of urls to be loaded, which will be processed in ascending
// order.  OrdReq_Callback is the callback to be used when the last 
// request is sent.  Up to that point it will basically loop back to itself.
function orderedRequestsCallback(result, OrdReq_loadList, OrdReq_Callback) {
    if (OrdReq_loadList.length > 1) {orderedRequests(OrdReq_loadList, OrdReq_Callback)}
    else {loadJSONDoc(OrdReq_loadList[0]).addCallback(OrdReq_Callback)}
}
function orderedRequests (OrdReq_loadList, OrdReq_Callback) {
    var thisRequest = OrdReq_loadList[0]
    OrdReq_loadList = OrdReq_loadList.slice(1)
    //bind is amazing, and the only way to avoid using Global variables.  Thanks MochiKit!!!
    var cb = bind(orderedRequestsCallback, self, undefined, OrdReq_loadList, OrdReq_Callback)
    loadJSONDoc(thisRequest).addCallback(cb)
}


function getStatus(get_all) {
    if (typeof(Sd) != "undefined") {Sd.cancel()}
    if (!status_break){
        if (status_next_update == true) {
            var stats = ""
            if (status_last_request < 1000) {status_last_request++}
            else {status_last_request = 0}
            if (!get_all) { stats = "?songid="+current_song_id+"&time="+current_play_time }
            Sd = loadJSONDoc("status"+stats).addCallback(displayStatus)
            status_next_update = false
            callLater(update_interval/2, function(){status_next_update = true})
        }
        else {
            var delayedStatus = function delayedStatus (d){if(status_next_update && status_last_request == d){getStatus()}}
            callLater(update_interval, delayedStatus, status_last_request)
        }
    }
}


function setvol(vol) {
    loadJSONDoc("setvol?vol="+vol)
    getStatus()
}


function control(action) {
    var d = loadJSONDoc("control?action="+action)
    
    if (action == "pause" || action == "play") {
        var myCallback = function (result) { 
            getStatus(true)
            callLater(update_interval, HLout, "controlHL")
        }
    }
    else { var myCallback = function (result) {getStatus()} }
    
    d.addCallback(myCallback)
}

function doseek(seek_to) {
    if (seeking) {
        loadJSONDoc("seek?seek_to="+seek_to)
        getStatus()
        if (seek_to < 0) {seek_to--}
        else { seek_to++ }
        callLater(update_interval, doseek, seek_to)
    }
}

function getBrowse(dir) {
    active_switch = "showBrowse"
    switchout("showBrowse")
    switchout("showNowPlaying")
    switchout("showSearch")
    d = loadJSONDoc("browsempd?dir="+dir)
    var done = function() { 
                             $("browselist").innerHTML = ""
                             removeBorder("BL")
                             d.addCallback(displayBrowse)
                         }
    stepOpacity("centerLeft", 1, 0.01, step_out_duration, done)
}


function getPlaylist(more_start, chunk) {
    var args = ""
    if (typeof(PLd) != "undefined") { PLd.cancel()}
    if (typeof(more_start) != "undefined" && typeof(more_start["ok"]) == "undefined") {
        args = "?start="+more_start
        if (typeof(chunk) != "undefined") {args = args + "&chunk="+chunk}
        PLd = loadJSONDoc("playlist"+args)
    }
    else {
        playlist = ""
        PLd = loadJSONDoc("playlist")
    }

    PLd.addCallback(displayPlaylist)
}


function getPlaylistChanges() {
    $("plLabel").innerHTML = "Updating Playlist..."
    if (typeof(playlist_version) == "undefined" || typeof(playlist_length) == "undefined") {getPlaylist()}
    else {
        if (typeof(PLd) != "undefined") { PLd.cancel()}
        PLd = loadJSONDoc("playlist_changes?version="+playlist_version+"&len_old="+playlist_length+"&start="+chunk_start+"&chunk="+chunk)
        PLd.addCallback(displayPlaylistChanges)
    }
}


function loadPlaylist (id) {
    $("playlist").innerHTML = "<br><center>Loading '"+id+"'...</center>"
    removeBorder("PL")
    loadJSONDoc("load?playlist="+id).addCallback(displayPlaylist);
}

function clearPlaylist() {
    if (typeof(PLd) != "undefined") { PLd.cancel()}
    playlist_changing = false
    loadJSONDoc("clearPlaylist").addCallback(displayPlaylist)
}


function getNowPlaying(l) {
    active_switch = "showNowPlaying"
    switchout("showBrowse")
    switchout("showNowPlaying")
    switchout("showSearch")
    replaceChildNodes("crumbtrail", "Loading Now Playing")
    if (typeof(l) != "undefined") {l = "?link="+l}
    else {l = ""}
    if (typeof(NPd) != "undefined") { NPd.cancel()}
    NPd = loadJSONDoc("nowplaying"+l)

    var done = function() { 
                             $("browselist").innerHTML = ""
                             removeBorder("BL")
                             NPd.addCallback(displayNowPlaying)
                         }
    stepOpacity("centerLeft", 1, 0.01, step_out_duration, done)
}


function getSearch(what, s) {
    active_switch = "showSearch"
    switchout("showBrowse")
    switchout("showNowPlaying")
    switchout("showSearch")
    if (s != "[cache]") {l = "Searching for '"+s+"'..."}
    else {l = "Loading Search Results"}
    replaceChildNodes("crumbtrail", l)
    Srchd = loadJSONDoc("getSearch?search_for="+s+"&search_what="+what)
    var done = function() { 
                            $("browselist").innerHTML = ""
                            removeBorder("BL")
                            Srchd.addCallback(displaySearch)
                        }
    stepOpacity("centerLeft", 1, 0.01, step_out_duration, done)
}


function updateMPD() {
    $("updb").innerHTML = "Updating Database..."
    BLout()
    el = $("bupdb_tablerow")
    el.onclick = ""
    el.onmouseover = ""
    el.onmouseout = ""
    setOpacity(el, 0.70)
    updb_called = true
    loadJSONDoc("updateMPD").addCallback(function(){getStatus()})
}


function browsePL() {
    if (typeof(PLd) != "undefined") { PLd.cancel()}
    loadJSONDoc("browsePL").addCallback(displayPL)
    $("playlist").innerHTML = "<br/><center>Loading Playlists...</center>"
    playlist_changing = false
}


function savePL() {
    var PLname = prompt("Please enter a name for this playlist","NewPlaylist")
    if (PLname != null) {loadJSONDoc("save?name="+PLname).addCallback(displayPlaylist)}
}


function addPlay(file) {
    $("plLabel").innerHTML = "Updating Playlist..."
    loadJSONDoc("addplay?song="+file).addCallback(getPlaylistChanges)
}

function set (action) {
    current_song_id = "none"
    loadJSONDoc("set?action="+action).addCallback(getPlaylistChanges)
    hideOptions()
}
