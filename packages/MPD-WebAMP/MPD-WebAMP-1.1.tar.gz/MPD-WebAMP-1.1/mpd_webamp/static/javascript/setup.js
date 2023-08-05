function init() {
    getThemes()
}

function adjustNormal() {
    $("fo").value = 400
    $("fi").value = 300
    $("fps").value = 40
    $("up").value = 330
    $("upsize").value = 100
    $("listsize").value = 1000
}

function adjustSlow() {
    $("fo").value = 500
    $("fi").value = 500
    $("fps").value = 10
    $("up").value = 500
    $("upsize").value = 20
    $("listsize").value = 20
}

function _me() {
    var u = window.location.toString()
    i = u.indexOf("setup") -1
    u = u.substr(0, i)
    return u
}

function applyThis() {
    u = _me()
    u += "?fadein="+$("fi").value
    u += "&fadeout="+$("fo").value
    u += "&fps="+$("fps").value
    u += "&delay="+$("up").value
    u += "&host="+$("host").value
    u += "&port="+$("port").value
    u += "&theme="+$("theme").value
    u += "&updatesize="+$("upsize").value
    u += "&listsize="+$("listsize").value
    window.location=u
}

function goBack() {
    window.location = _me()
}

function testConn() {
    loadJSONDoc("../testConn?port="+$("port").value+"&host="+$("host").value).addCallback(testResult)
}

function testResult(r) {
    $("stats").innerHTML = "<br />"+r["stats"]
}

function getThemes() {
    loadJSONDoc("../getThemes").addCallback(themeResult)
}

function themeResult(r){
    $("theme").innerHTML = r["themeList"]
}