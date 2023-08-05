<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<link rel="stylesheet" type="text/css" href="/static/themes/${theme}/style.css"/>
	<script type="text/javascript" src="/tg_js/MochiKit.js"></script>
	<script type="text/javascript">
	    var update_interval = $update_int
	    var step_out_duration = $fadeOut
	    var step_in_duration = $fadeIn
	    var step_interval = 1 / $fps
	    var font_size = '$font'
            var last = '$last'
            var theme = '$theme'
	</script>
	<script type="text/javascript" src="/static/javascript/amp.js"></script>
    <script type="text/javascript" src="/static/javascript/async_request.js"></script>
	<script type="text/javascript" src="/static/javascript/async_receive.js"></script>
</head>
<body onload="setTimeout('init();',200);" >
	<div id="PLmore" class="options">
    	    <div id="PLmore-inner" class="options-inner">
    	        <div id="PLmore-body" class="options-body">
    	            <span id="more_play" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'" onclick="PL_click(null, null, 'play'); hidePLmore()">&nbsp;&nbsp;Play Now</span><br/>
    	            <span id="more_sort" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'" onclick="hidePLmore(); PL_action='sort'; PL_click(null, null, 'sort')">&nbsp;&nbsp;Move To...</span><br/>
    	            <span id="more_remove" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'" onclick="PL_click(null, null, 'remove'); hidePLmore()">&nbsp;&nbsp;Remove</span><br/>
    	            <div class="options-divider"></div>
    	            <span onclick="hidePLmore()" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'">&nbsp;&nbsp;Cancel</span>
    	        </div>
    	    </div>
    	</div>
    	
    	<div id="BLmore" class="options">
    	    <div id="BLmore-inner" class="options-inner">
    	        <div id="BLmore-body" class="options-body">
    	            <span id="more_append" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'" onclick="BL_click(null, null, 'append'); hideBLmore()">&nbsp;&nbsp;Add to Playlist</span><br/>
    	            <span id="more_playnow" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'" onclick="BL_click(null, null, 'playnow'); hideBLmore()">&nbsp;&nbsp;Play Now</span><br/>
    	            <div class="options-divider"></div>
    	            <span onclick="hideBLmore()" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'">&nbsp;&nbsp;Cancel</span>
    	        </div>
    	    </div>
    	</div>

	<div id="controlHL" onmouseout="HLout('controlHL')"><div id="controlHL-inner"><div id="controlHL-body"></div></div></div>

	<div id="options" class="options">
	    <div id="options-inner" class="options-inner">
	        <div id="options-body" class="options-body">
	            <span onclick="set('normal')" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'">Playback: Normal</span>
	            <span onclick="set('random')" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'">Playback: Random</span>
	            <span onclick="set('shuffle')" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'">Shuffle Playlist</span>
	            <div class="options-divider"></div>
	            <span onclick="hideOptions()" onmouseover="this.style.fontWeight='bold'" onmouseout="this.style.fontWeight='normal'">Cancel</span>
	        </div>
	    </div>
	</div>
	
	<div id="topBar" class="topBar">
	   <div id="showBrowse" onmousedown="getBrowse('[cache]')" onmouseover="switchover(this.id)" onmouseout="switchout(this.id)"> 
	       <div id="showBrowse-l" class="switch-l switch-l-back"></div>
	       <div id="showBrowse-m" class="switch-m switch-m-back"><div class="label">Browse Files</div></div>
	       <div id="showBrowse-r" class="switch-r switch-r-back"></div>
	   </div>
	   <div id="showNowPlaying" onmousedown="getNowPlaying()" onmouseover="switchover(this.id)" onmouseout="switchout(this.id)"> 
	       <div id="showNowPlaying-l" class="switch-l switch-l-back"></div>
	       <div id="showNowPlaying-m" class="switch-m switch-m-back"><div class="label">Now Playing</div></div>
	       <div id="showNowPlaying-r" class="switch-r switch-r-back"></div>
	   </div>
	   <div id="showSearch" onmousedown="getSearch('[cache]', '[cache]')" onmouseover="switchover(this.id)" onmouseout="switchout(this.id)"> 
	       <div id="showSearch-l" class="switch-l switch-l-back"></div>
	       <div id="showSearch-m" class="switch-m switch-m-back"><div class="label">Search</div></div>
	       <div id="showSearch-r" class="switch-r switch-r-back"></div>
	   </div>
            <div id="quickSearchCont">
                <div align="center"><input halign="center" id="quickSearch" type="text" class="disabled" onkeydown="quickSearch(this.value, event)" name=" Type here to search" onfocus="searchOver(this)" onBlur="searchOut(this)" value=" Type here to search"/>
                <input id="ghost" type="hidden"/></div>
            </div>
	   
	   <div id="openPL" onmouseover="switchover(this.id)" onmousedown="browsePL()" onmouseout="switchout(this.id)">
	       <div id="openPL-l" class="switch-l switch-l-back"></div>
	       <div id="openPL-m" class="switch-m switch-m-back"><div class="label">Load Playlist</div></div>
	       <div id="openPL-r" class="switch-r switch-r-back"></div>
	   </div>

	   <div id="clearPL" onmouseover="switchover(this.id)" onclick='clearPlaylist()' onmouseout="switchout(this.id)">
	       <div id="clearPL-l" class="switch-l switch-l-back"></div>
	       <div id="clearPL-m" class="switch-m switch-m-back"><div class="label">Clear Playlist</div></div>
	       <div id="clearPL-r" class="switch-r switch-r-back"></div>
	   </div>

	   <div id="goSetup" onmouseover="switchover(this.id)" onclick="goSetup()" onmouseout="switchout(this.id)">
	       <div id="goSetup-l" class="switch-l switch-l-back"></div>
	       <div id="goSetup-m" class="switch-m switch-m-back"><div id="setup_icon" title="Setup">&nbsp;</div></div>
	       <div id="goSetup-r" class="switch-r switch-r-back"></div>
	   </div>
	</div>
	
    <div  id="centerLeftHead" class="centerLeftHead">
        <div id="home" onclick="getBrowse('/')"/>
        <div id="back" />
        <div id="crumbtrail"></div>
        <div id="addAll"/>
    </div>

	<div id="centerLeft" class="centerLeft">
        <div id="BLborderT" class="borderT"><div id="BLborderTinside" class="borderTinside"></div></div>
	    <div id="BLborderR" class="borderR"><div id="BLborderRinside" class="borderRinside"></div></div>
	    <div id="BLborderB" class="borderB"><div id="BLborderBinside" class="borderBinside"></div></div>
	    <div id="BLborderL" class="borderL"><div id="BLborderLinside" class="borderLinside"></div></div>
        <div id="browselist"></div>
	</div>
	
	<div id="centerDivider" class="centerDivider">
	    <div  class="centerDividerL"></div>

	    <div  class="centerDividerR"></div>
	</div>
	
	<div id="playlistHeader" class="centerRightHead">
	    <div class="playlistHeaderContents"><div id="currentPlaylist"><div id="PLoptions" onclick="showOptions()" /><span id="optLabel" onclick="showOptions()">Options</span><div id="PLsave" onclick="savePL()"/><center><span id="plLabel">Playlist</span></center></div></div>
            <div id="choosePlaylist" class="playlistHeaderContents" style='height:0px;Z-index:10'><center>Select Playlist to load...</center></div>
	</div>
		
	<div id="centerRight" class="centerRight">	    
        <div id="PLborderT" class="borderT"><div id="PLborderTinside" class="borderTinside"></div></div>
        <div id="PLborderR" class="borderR"><div id="PLborderRinside" class="borderRinside"></div></div>
        <div id="PLborderB" class="borderB"><div id="PLborderBinside" class="borderBinside"></div></div>
        <div id="PLborderL" class="borderL"><div id="PLborderLinside" class="borderLinside"></div></div>
	<div id="insertArrow"/>
   	
	   <div id="playlist"><br/><center>Loading Playlist...</center></div>
	</div>


	<div id="bottomBar" class="bottomBar">
	   <div id="controls">
                <div id="prev" class="base" onclick="control('prev')" onmouseover="this.className='highlight'" onmousedown="this.className='pressed'" onmouseout="this.className='base'"/>
                <div id="stop" class="base" onclick="control('stop')" onmouseover="this.className='highlight'" onmousedown="this.className='pressed'" onmouseout="this.className='base'"/>
                <div id="pause" class="base" onclick="control('pause')" onmouseover="this.className='highlight'" onmousedown="this.className='pressed'" onmouseout="this.className='base'" />
                <div id="play" class="base" onclick="control('play')" onmouseover="this.className='highlight'" onmousedown="this.className='pressed'" onmouseout="this.className='base'"/>
                <div id="next" class="base" onclick="control('next')" onmouseover="this.className='highlight'" onmousedown="this.className='pressed'" onmouseout="this.className='base'"/></div>
		<img id="vol-back" class="volume" src="/static/themes/default/vol-inactive.png" usemap="#volmap"/>
		<div id="vol-front"><img class="volume" src="/static/themes/default/vol-active.png" usemap="#volmap"/></div>
		<map id="volmap" name="volmap" class="volume">
			<area shape="rectangle" coords="0 0 5 32" onmouseup="setvol(0)"></area>
			<area shape="rectangle" coords="6 0 10 32" onmouseup="setvol(10)"></area>
			<area shape="rectangle" coords="11 0 15 32" onmouseup="setvol(20)"></area>
			<area shape="rectangle" coords="16 0 20 32" onmouseup="setvol(30)"></area>
			<area shape="rectangle" coords="21 0 25 32" onmouseup="setvol(40)"></area>
			<area shape="rectangle" coords="26 0 30 32" onmouseup="setvol(50)"></area>
			<area shape="rectangle" coords="31 0 35 32" onmouseup="setvol(60)"></area>
			<area shape="rectangle" coords="36 0 40 32" onmouseup="setvol(70)"></area>
			<area shape="rectangle" coords="41 0 45 32" onmouseup="setvol(80)"></area>
			<area shape="rectangle" coords="46 0 50 32" onmouseup="setvol(90)"></area>
			<area shape="rectangle" coords="51 0 55 32" onmouseup="setvol(100)"></area>
		</map>
		
	    <div id="song-details">
	        <div id="song_calc" class="song_big"></div>
	        <div id="song_container" onclick="gotoCurrentSong()">
    	        <div id="song" class="song_big"></div>
	        </div>
	        <img id="song_time_spacer" src="/static/themes/${theme}/button-back.png" />
	        <div id="time_container">
	            <div style="position:absolute; left: 0px; width: 1px"></div>
		        <div id="seek-backward" class="base" onmouseover="this.className='highlight'" onmousedown="this.className='pressed';mpdseek(-2)" onmouseup="this.className='highlight'; seeking=false" onmouseout="this.className='base'"/>
	            <div id="time" class="song_big"></div>
	            <div id="seek-forward" class="base" onmouseover="this.className='highlight'" onmousedown="this.className='pressed';mpdseek(2)" onmouseup="this.className='highlight'; seeking=false" onmouseout="this.className='base'"/>
	        </div>	        
        </div>       
        
	</div>
	
</body>
</html>
