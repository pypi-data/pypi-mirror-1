<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<link rel="stylesheet" type="text/css" href="/static/themes/${theme}/style.css"/>
        <script type="text/javascript" src="/tg_js/MochiKit.js"></script>
	<script type="text/javascript" src="/static/javascript/setup.js"></script>
        <style>
            Table {
                width: auto; 
                padding: 10px;
                margin-left: 0px;
                margin-right: auto;
            }
            TD {padding: 2px}
            Body {overflow: auto}
        </style>
</head>
<body onload="init()">
    <br />
    <input type="button" onclick="goBack()" value="Cancel" />&nbsp;&nbsp;
    <input type="button" onclick="applyThis()" value="Load MPD WebAMP with these settings"/>
    <br />
    <br /> 
    <hr />
    <h1>Theme</h1>
    <table>
        <tr><td align="right"><b>Theme:&nbsp;&nbsp;</b></td>
            <td><select id="theme"></select></td>
            <td><input type="button" onclick="getThemes()" value="Refresh List" /></td>
        </tr>
    </table>
    <br />
    <br />
    <hr />
    <h1>Music Player Daemon Connection</h1>
    <table>
        <tr><td align="right"><b>MPD address:&nbsp;&nbsp;</b></td><td><input type="text" id="host" value="$host" /></td></tr>
        <tr><td align="right"><b>MPD port:&nbsp;&nbsp;</b></td><td><input type="text" id="port" value="$port" /></td></tr>
        <tr><td align="right"></td><td><input type="button" onclick="testConn()" value="Test Connection" /></td></tr>
    </table>
    <div id="stats"></div>
    <br />
    <br />
    <hr />
    <h1>Performance</h1>
    <input type="button" onclick="adjustSlow()" value="Adjust for slow PCs (i.e. 600MHz cpu)" />&nbsp;&nbsp;
    <input type="button" onclick="adjustNormal()" value="Load default settings" /><br /><br />
    <table>
        <tr><td align="right" width="300px"><b>Fade Out duration (in milliseconds):&nbsp;&nbsp;</b></td><td><input type="text" id="fo" value="$fadeOut" />&nbsp;&nbsp;</td>
            <td>Fade out time for animations.</td></tr>
        <tr><td align="right"><b>Fade In duration (in milliseconds):&nbsp;&nbsp;</b></td><td><input type="text" id="fi" value="$fadeIn" />&nbsp;&nbsp;</td>
            <td>Fade in time for animations, also used for menu slide ins.</td></tr>
        <tr><td align="right"><b>Frames Per Second:&nbsp;&nbsp;</b></td><td><input type="text" id="fps" value="$fps" />&nbsp;&nbsp;</td>
            <td>Reasonable valus are 10 - 60, if set higher than your PC can handle, this will result in uneven transitions.</td></tr>
        <tr><td align="right"><b>Update delay interval (in milliseconds):&nbsp;&nbsp;</b></td><td><input type="text" id="up" value="$update_int" />&nbsp;&nbsp;</td>
            <td>Time between status updates, too high and the time counter will not flow smoothly, anything under 200ms would just waste resources.</td></tr>
        <tr><td align="right"><b>Playlist Updates batch size:&nbsp;&nbsp;</b></td><td><input type="text" id="upsize" value="$upsize" />&nbsp;&nbsp;</td>
            <td>Size of Playlist chunk to grab in each fetch before pausing for other events.  Hgher values result in a faster playlist update/load.  Lower values result in a more responsive interface while playlist is loading.</td></tr>
        <tr><td align="right"><b>Playlist maximum results:&nbsp;&nbsp;</b></td><td><input type="text" id="listsize" value="$listsize" />&nbsp;&nbsp;</td>
            <td>Maximum playlist items to show at once.  0 = no limit.</td></tr>
    </table>
    <br />
    <br />
    <hr />
    <br />
    <input type="button" onclick="goBack()" value="Cancel" />&nbsp;&nbsp;
    <input type="button" onclick="applyThis()" value="Load MPD WebAMP with these settings"/>
    <br />
    <br /> 
</body>
</html>