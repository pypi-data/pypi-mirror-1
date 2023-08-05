var active_switch = "showBrowse"
var PL_moveid = "none"
var PL_action = ""

var mouseX
var mouseY
var shift_key_down = false

var NPd
var Srchd
var Sd
var status_next_update = true
var status_last_request = 0
var key_next_update = true
var seeking = false
var inputfocus = false
var select_start = -1
var select_end = -1
var select_type = ""
var moreOpen = false
var current_song_id = "init"
var current_play_time = ""
var current_vol = 0
var updb_called = false

var PLd
var playlistLoading = false
var playlist = ""
var playlist_version = -1
var playlist_length
var chunk = 0
var chunk_start = 0
var playlist_changing = false
var status_break = true


function init() {
    if (font_size != "normal") {
        $("centerLeft").style.fontSize = font_size+"px"
        $("centerRight").style.fontSize = font_size+"px"
    }
    document.addEventListener("mousemove", function (e) {mouseX = e.pageX;mouseY = e.pageY;}, true)
    document.onkeypress = keyPress
    document.onkeydown = keyDown
    document.onkeyup = keyUp
    setOpacity("options", 0)
    setOpacity("centerLeft", 0.01)
    switch (last) {
        case "browse":
            setSwitch("showBrowse", "active")
            getBrowse("[cache]")
            break;
        case "lyrics":
            active_switch = "showNowPlaying"
            setSwitch("showNowPlaying", "active")
            getNowPlaying()
            break;
        case "search":
            active_switch = "showSearch"
            setSwitch("showSearch", "active")
            getSearch("[cache]", "[cache]")
            break;
    }
    getStatus(true)
    getPlaylist()
    callLater(update_interval*15, heartbeat, 0)
}

//Kickstart broken status loops
function heartbeat(l){
    if (status_next_update && !playlistLoading) {
        if (status_last_request==l) {getStatus()}
    }
    callLater(update_interval*15, heartbeat, status_last_request)
}
function esc(s){return encodeURIComponent(s)}
function isDigit(num) {
	if (num.length>1){return false;}
	var string="1234567890";
	if (string.indexOf(num)!=-1){return true;}
	return false;
	}
function isInteger(val){
    for(var i=0;i<val.length;i++){
            if(!isDigit(val.charAt(i))){return false;}
            }
    return true;
}


function goSetup() {
    u = window.location.toString()
    i = u.indexOf("?")
    if (i > 0) {u = u.substr(0, i)}
    u += "setup/"
    window.location = u
}

function stepOpacity(elem, start, end, duration, myLoad, myCallback, fx_start) {
    var d = new Date
    
    if (typeof(fx_start) == "undefined" ) {
        var fx_start = d.getTime()
        callLater(step_interval, stepOpacity, elem, start, end, duration, myLoad, myCallback, fx_start)
    }
    else { 
        var now = d.getTime()
        var p = (now - fx_start) / duration    
        var t  =  end - start
        if (p > 1) {p=1}
        var o = (t * p) + start
        setOpacity(elem, o)
        if (p != 1) { callLater(step_interval, stepOpacity, elem, start, end, duration, myLoad, myCallback, fx_start) }
        else {
            if (typeof(myLoad) != "undefined") {
                if (typeof(myCallback) != "undefined") {
                    myLoad.addCallback(myCallback)
                }
                else { callLater((step_in_duration/3000), myLoad) }
            }
        }
    }
}    

function stepHeight(elem, start, end, duration, myLoad, myCallback, fx_start) {
    var d = new Date
    
    if (typeof(fx_start) == "undefined" ) {
        var fx_start = d.getTime()
        callLater(step_interval, stepHeight, elem, start, end, duration, myLoad, myCallback, fx_start)
    }
    else { 
        var now = d.getTime()
        var p = (now - fx_start) / duration
        if (p > 1) {p =1}
        var t  =  end - start
        var h = (t * p) + start
        //alert("end="+end+", p="+p+", h="+h)
        $(elem).style.height = h+"px"
        if (p != 1) { callLater(step_interval, stepHeight, elem, start, end, duration, myLoad, myCallback, fx_start) }
        else {
            if (typeof(myLoad) != "undefined") {
                if (typeof(myCallback) != "undefined") { myLoad.addCallback(myCallback) }
                else { myLoad() }
            }
        }
    }
} 


function mpdseek(seek_to) {
    seeking = true
    doseek(seek_to)  
}


function showOptions () { 
    //setOpacity("options", 0)    
    //$("options").style.height = "76px"
    var d = elementDimensions("options")
    if (d["h"] == 0) {
        $("optLabel").style.color = "white"
        setOpacity("options", 1)
        stepHeight("options", 1, 94, step_in_duration*0.75)
    }
    else {hideOptions()}
}


function hideOptions () { 
    //setOpacity("options", 1)
    $("optLabel").style.color = "#777"
    var done = function (){$("options").style.height = "0px"}
    stepOpacity("options", 1, 0, step_out_duration*1.5, done)
}


function cancelContext(event) {
    event.cancelBubble = true
    event.cancel = true
    event.returnValue = false
}


function showPLmore (event, id) {
    var b = 2
    if (event != null) {
        b = event.button
        if (b == 2 || b == 3) {
            event.cancelBubble = true
            event.cancel = true
            event.returnValue = false
        }
    }

    if (b == 2 || b == 3) {
        INTid = parseInt(id.substring(1))
        if (INTid < select_start || INTid > select_end) {
            _select("p", INTid)
        }
        var d = elementDimensions("PLmore")
        if (d["h"] == 0) {
            var myStyle = {"top": (mouseY-10)+"px", "left": (mouseX-5)+"px", "width": "95px"}
            moreOpen = true
            updateNodeAttributes("PLmore", {"style": myStyle})
            setOpacity("PLmore", 1)
            stepHeight("PLmore", 1, 80, step_in_duration*0.75)
        }
        else {hidePLmore()}
    }
}

function hidePLmore () { 
    moreOpen = false
    var done = function (){updateNodeAttributes("PLmore", {"style": {"height": "0px", "top": "0px", "left": "0px"}})}
    stepOpacity("PLmore", 1, 0, step_out_duration*1.5, done)
}


function showBLmore (event, id) {
    var b = 2
    if (event != null) {
        b = event.button
        if (b == 2 || b == 3) {
            event.cancelBubble = true
            event.cancel = true
            event.returnValue = false
        }
    }

    if (b == 2 || b == 3) {
        id = parseInt(id)
        if (id < select_start || id > select_end) {_select("b", id)}
        var d = elementDimensions("BLmore")
        if (d["h"] == 0) {
            var myStyle = {"top": (mouseY-10)+"px", "left": (mouseX-5)+"px", "width": "120px"}
            moreOpen = true
            updateNodeAttributes("BLmore", {"style": myStyle})
            setOpacity("BLmore", 1)
            stepHeight("BLmore", 1, 65, step_in_duration*0.75)
        }
        else {hideBLmore()}
    }
}


function hideBLmore () { 
    moreOpen = false
    var done = function (){updateNodeAttributes("BLmore", {"style": {"height": "0px", "top": "0px", "left": "0px"}})}
    stepOpacity("BLmore", 1, 0, step_out_duration*1.5, done)
}


function setSwitch(id, state) {
    $(id+"-l").className = "switch-l switch-l-"+state
    $(id+"-m").className = "switch-m switch-m-"+state
    $(id+"-r").className = "switch-r switch-r-"+state
}

function switchover(id) {if(id != active_switch){setSwitch(id, "highlight")}}

function switchdown(id) {setSwitch(id, "active")}

function switchout(id) {
    if (id == active_switch) {setSwitch(id, "active")}
    else {setSwitch(id, "back")}
}

function buttonover(id) {
    elem.className = "highlight"
}

function addBorder(L, id) {
    var c = Color.fromBackground(id)
    var myHighlight = c.lighterColorWithLevel(0.3)
    var myShadow = c.darkerColorWithLevel(0.2)
   
    $(L+"borderT").style.backgroundColor = myHighlight
    $(L+"borderB").style.backgroundColor = myHighlight
    $(L+"borderL").style.backgroundColor = myHighlight
    $(L+"borderR").style.backgroundColor = myHighlight
    
    $(L+"borderTinside").style.backgroundColor = myShadow
    $(L+"borderBinside").style.backgroundColor = myShadow
    $(L+"borderLinside").style.backgroundColor = myShadow
    $(L+"borderRinside").style.backgroundColor = myShadow
    
    var dim = elementDimensions(id)
    var pos = elementPosition(id, L+"borderT")
    //Konqueror reports table row height incorrectly, use the height of the cell
    dim["h"] = elementDimensions(TRobject($(id)).id)["h"]

    var mystyleT = {"height" : "2px",  "width" : dim["w"]+2+"px", "top" : pos["y"]-2+"px", "left" : pos["x"]-1+"px"}
    var mystyleB = {"height" : "2px",  "width" : dim["w"]+2+"px", "top" : pos["y"]+dim["h"]+"px", "left" : pos["x"]-1+"px"}
    var mystyleL = {"height" : dim["h"]+4+"px",  "width" : "2px", "top" : pos["y"]-2+"px", "left" : pos["x"]-1+"px"}
    var mystyleR = {"height" : dim["h"]+4+"px",  "width" : "2px", "top" : pos["y"]-2+"px", "left" : pos["x"]+dim["w"]-1+"px"}
 
    updateNodeAttributes(L+"borderT",{"style": mystyleT})
    updateNodeAttributes(L+"borderB", {"style": mystyleB})
    updateNodeAttributes(L+"borderL", {"style": mystyleL})
    updateNodeAttributes(L+"borderR", {"style": mystyleR})
}

function removeBorder (L) {
    var myStyle = {"height" : "0px", "width" : "0px", "top" : "0px", "left" : "0px"}
    updateNodeAttributes(L+"borderT", {"style": myStyle})
    updateNodeAttributes(L+"borderB", {"style": myStyle})
    updateNodeAttributes(L+"borderL", {"style": myStyle})
    updateNodeAttributes(L+"borderR", {"style": myStyle})
    updateNodeAttributes("insertArrow", {"style": myStyle})
}

function showInsert(id) {
    var i = parseInt(id.substr(1))
    var ok = true
    if (PL_moveid != "none") {
        if (PL_moveid == "selection") {
            if (i >= select_start && i <= select_end) {ok = false}
        }
        else {if (PL_moveid == i) {ok = false}}
    }
    if (ok) {
        var tr = $(id+"_tablerow")
        var t = 0
        var h = 0
        var pos = elementPosition(tr, "insertArrow")
        if (i < parseInt(select_start)) { t = pos["y"]-10+"px"}
        else {
            h = elementDimensions(id)["h"]
            t = pos["y"]+h-8+"px"
        }
        var myStyle = {"height":"18px", "width":"18px","top":t,"left":pos["x"]-3+"px"}
        updateNodeAttributes("insertArrow", {"style": myStyle})
    }
}


function BLover(id) {
    if (moreOpen) { hideBLmore() }
    removeBorder("BL")
    addBorder("BL", id)
}

function BLout(id) {
    if (moreOpen == false) {
        removeBorder("BL")
    }
}
    
function PLover(id) {
    if (moreOpen) { hidePLmore() }
    removeBorder("PL")
    if (PL_moveid == "none") {addBorder("PL", id+"_tablerow")}
    else {showInsert(id)}
}

function PLout(id) {
    if (moreOpen == false) {removeBorder("PL")}
}

function loadPLover(id) {
    if (moreOpen) {hidePLmore()}
    removeBorder("PL")
    id = id+"_tablerow"
    addElementClass(id, "sort")
    addBorder("PL", id)
}


function loadPLout(id) {
    removeElementClass(id+"_tablerow", "sort")
    removeBorder("PL")
}


function remPLover(id) {
    if (moreOpen) { hidePLmore() }
    removeBorder("PL")
    id = id+"_tablerow"
    addElementClass(id, "remove")
    addBorder("PL", id)
}

function remPLout(id) {
    removeElementClass(id+"_tablerow", "remove");
    removeBorder("PL");
}


function searchOver(elem) {
    swapElementClass(elem.id, "disabled", "enabled")
    if (elem.name == " Type here to search") { elem.value = "" }
    else { elem.value = elem.name }
    inputfocus = true
}


function searchOut(elem) {
    swapElementClass(elem.id, "enabled", "disabled")
    elem.name = elem.value
    elem.value = " Type here to search"
    inputfocus = false
}


function _select(type, id) {
    select_start = parseInt(select_start)
    select_end = parseInt(select_end)
    //first deselect previous selection
    if (select_start >= 0) {
        for (index=select_start;index<=select_end;index++) {
            removeElementClass(select_type+index+"_tablerow", "sort");
        }
    }
    select_type = type
    
    if (typeof(id) != "undefined") {
        if (shift_key_down) {
            //the range must always go from lowest to highest
            var s = [select_start, select_end, id]
            select_start = listMin(s)
            select_end = listMax(s)
        }
        else {
            select_start = id
            select_end = id
        }
        //highlight new selection
        for (index=select_start;index<=select_end;index++) {
            addElementClass(select_type+index+"_tablerow", "sort");
        } 
    }
    else {
        select_start = -1
        select_end = -1
        select_type = ""
    }
}


function addAllSR() {
    e = ($("browselist_table").rows.length / 2) - 1
    if (e >= 0) {
        select_start = 0
        select_end = e
        BL_click(null, e, "append")
    }
}


function TRobject (elem) {
    try {var elem = elem.childNodes[0]}
    catch (err) {var elem = elem.childNodes[1]}
    item = new Object()
    item.filefolder = ""
    item.id = ""
    while (elem) {
        try {
            if (item.filefolder == "") {
                if (elem.hasAttribute("class")) {item.filefolder = elem.getAttribute("class")}
            }
            else {
                if (elem.hasAttribute("id")) {
                    item.id=elem.getAttribute("id")
                }
            }
        }
        catch (err){}
        if (item.filefolder == "" || item.id == "") {elem = elem.nextSibling}
        else {elem = null}
    }
    return item
}


function BL_click (event, id, action) {
    if (event != null) {
        event.cancelBubble = true
        event.cancel = true
        event.returnValue = false
    }
    if (id == null) {id = select_start}
    id = parseInt(id)
    if (typeof(action) == "undefined" || action == "") {
        if (select_start == select_end && select_start == id && select_type == "b") {
            action = "smart"
        }
        else {action = ""}    
        _select("b", id)
        BLover("b"+id+"_tablerow")
    }
    
    if (action == "playnow") {
        var play = "True"
        action = "append"
    }
    else {var play = "False"} 
    
    var item = TRobject($("b"+id+"_tablerow"))
    switch (action) {
        case "append":
            var more = "False"
            
            if (select_start == select_end) {
                $("plLabel").innerHTML = "Updating . . ."
                loadJSONDoc("addplay?song="+esc(item.id)+"&more=False&play="+play).addCallback(getPlaylistChanges)
            }
            else {
                var d = new Array()
                playlist_changing = true
                $("plLabel").innerHTML = "Updating Playlist..."
                for (index=select_start;index<=select_end;index++) {
                    item = TRobject($("b"+index+"_tablerow"))
                    if (index != select_end) {more = "True"}
                    else {more = "False"}
                    if (index != select_start) {play = "False"}
                    d.push("addplay?song="+esc(item.id)+"&more="+more+"&play="+play)
                } 
                orderedRequests(d, getPlaylistChanges)
                _select("b")
            }  
            _select("b")  
            break;
        case "smart":
            if (item.filefolder == "icon_file" || item.filefolder == "file") {
                $("plLabel").innerHTML = "Updating Playlist..."
                loadJSONDoc("addplay?song="+esc(item.id)+"&more=False&play="+play).addCallback(getPlaylistChanges)        
            }
            else {getBrowse(esc(item.id))}
            _select("b")
            break;
            
        default:
            break;
    }
}



function PL_click(event, id, action) {
    if (id == null) {id = select_start}
    id = parseInt(id)
    if (typeof(action) == "undefined") {action = PL_action}
    if (event != null){
        event.cancelBubble = true
        event.cancel = true
        event.returnValue = false
        if (action == "") {
            if (select_start == select_end && select_start == id && select_type == "p") {action = "play"}
        }
        if (action != "sort" && action != "remove") {_select("p", id); PLover("p"+id)}
    }

    switch (action){
        case "play":
            loadJSONDoc("playnow?myid="+id);
            getStatus()
            _select("p")
            break;
        case "remove":
            playlist_changing = true
            for (index=select_start;index<=select_end;index++) {
                if (index == select_end) {
                    loadJSONDoc("remove?myid="+select_start).addCallback(getPlaylistChanges)
                } 
                else { loadJSONDoc("remove?myid="+select_start) }
            }
            _select("p")
            break;
        case "sort":
            if (select_start == select_end) {
                if (PL_moveid == "none") {
                    PL_moveid = id;
                    $("p"+id+"_left").innerHTML = ""
                    $("p"+id+"_left").className = "icon_sort"
                    setOpacity(id, 0.6);
                    PL_action = "sort"
                }
                else {
                    if (PL_moveid == id) {
                        l = $("p"+id+"_left")
                        l.className = "icon_PL"
                        l.innerHTML = (id+1)+"."
                        PL_moveid = "none"
                        PL_action = ""
                        _select("p")
                    }
                    else {
                        playlist_changing = true
                        loadJSONDoc("move?fromid="+PL_moveid+"&toid="+id).addCallback(getPlaylistChanges)
                        PL_moveid = "none";
                        PL_action = ""
                        _select("p")
                    }
                }
            }
            else {
                if (PL_moveid == "selection") {
                    if (id >= select_start && id <= select_end) {
                        for (index=select_start;index<=select_end;index++) {
                            var l = $("p"+index+"_left")
                            l.className = "icon_PL"
                            l.innerHTML = (index+1)+"."
                        }
                        PL_moveid = "none"
                        PL_action = ""
                        _select("p")
                    }
                    else {
                        playlist_changing = true
                        var movefrom = select_start
                        var moveto = id
                        var d = new Array()
                        for (index=select_start;index<=select_end;index++) {
                            d.push("move?fromid="+movefrom+"&toid="+moveto)
                            if (id < select_start) {movefrom++;moveto++}
                        } 
                        orderedRequests(d, getPlaylistChanges)
                        PL_moveid = "none"
                        PL_action = ""
                        _select("p")
                    }
                }
                else {
                    PL_moveid = "selection"
                    for (index=select_start;index<=select_end;index++) {
                        $("p"+index+"_left").innerHTML = ""
                        $("p"+index+"_left").className = "icon_sort"
                    }
                    PL_action = "sort"
                }
            }
            break;
        default:
            break;
    }
}

function quickSearch(s, e) {
    if (e.keyCode == 13) {
        getSearch("any", s)
        $("ghost").focus()
    }
}

function fullSearch(s, e) {
    if (e.keyCode == 13) {
        getSearch($("select_what").value, s)
    }
}
function gotoWait() { 
    if(!playlistLoading){gotoCurrentSong()}
    else {callLater(0.5, gotoWait)}
}
function gotoCurrentSong() {
    if (isInteger(current_song_id)) {
            var dim = elementDimensions("PLborderT")
            if (dim["h"] == 0) {
                csi = parseInt(current_song_id)
                var e = $("p"+csi+"_tablerow")
                if (e != null) {
                    setElementClass(e, "playing")
                    if (csi > 0) {csi--}
                    var pos = elementPosition("p"+csi+"_tablerow", "p0")
                    $("centerRight").scrollTop = pos["y"] + 5
                }
                else {
                    getPlaylist(csi, 1)
                    callLater(1, gotoWait)
                }
            }
    }
}

function keyPress(event) {
    if (!inputfocus) {
        switch(event.keyCode) {
            case 37:
                if (key_next_update) {
                    loadJSONDoc("seek?seek_to=-5")
                    getStatus()
                    key_next_update = false
                    setTimeout("key_next_update = true", update_interval*1000)
                }
                return false;
                break;
            case 39:
                if (key_next_update) {
                    loadJSONDoc("seek?seek_to=5")
                    getStatus()
                    key_next_update = false
                    setTimeout("key_next_update = true", update_interval*1000)
                }
                return false;
                break;
            case 38:
                if (key_next_update) {
                    setvol("up");
                    key_next_update = false
                    setTimeout("key_next_update = true", update_interval*500)
                }
                return false;
                break;
            case 40:
                if (key_next_update) {
                    setvol("down");
                    key_next_update = false
                    setTimeout("key_next_update = true", update_interval*500)
                }
                return false;
                break;
        }
    }
}


function keyDown(event) {
    if (!inputfocus) {
        switch(event.keyCode) {
            case 16:
                shift_key_down = true;
                event.cancelBubble = true
                event.cancel = true
                break;
        }
    }
}


function keyUp(event) {
    if (!inputfocus) {
        switch(event.keyCode) {
            case 16:
                shift_key_down = false;
                break;
        }
    }
}

