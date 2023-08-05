Quick Start:

import findlyrics

    #The quick and lazy way
    def getLyrics():
        my_song = dict(artist="Tom Waits", title="Clap Hands", album="Rain Dogs")
        lazy = findlyrics.Song(my_song).quickSearch().table
        return lazy

    #Or you could get more involved and deal with multiple search reults...
    def getLyrics():
        f = findlyics.Song()
        f.artist = ...
        f.album = ...
        f.title = ...
        f.search()
        r = f.SearchResults.parse(0).table
        rc = f.SearchResults.count
        if (rc > 1):
            alt = "<br><div style='padding:10px'><b>Full Lyrics Search Results:</b><br><br>"
            for i in range(0, rc-1):
                alt += "<a href='javascript:getNowPlaying(\""+f.SearchResults.links[i]+"\")'>"
                alt += f.SearchResults.labels[i]+"</a><br>"
            alt += "</div>"
            r += alt


Attributes:
  class Song:
    Song.artist
    Song.album
    Song.title
    Song.SearchResults.count        Number of results found from lyrics search.
    Song.SearchResults.links        List of links to lyrics search results.
    Song.SearchResults.labels       List of labels for links (from original links on findlyrics.com)
    Song.SearchResults.similarXML   similar.xml file from audioscrobbler, similar artists.
    Song.SearchResults.albumXML     XML file from musicbrainz for the album

  class ParseResults:
    ParseResults.table          All the data in a <table>.
    ParseResults.lyrics         Lyrics in HTML form, wrapped in <div id='lyrics'>.
    ParseResults.image          Album art as <img>, usually 240x240, but if not available it will use smaller,
                                or even use artist picture from last.fm if no valid album image is found.
                                Wrapped in <div id='album' class='art'><center><img src=...></center></div>.
    ParseResults.similar        Top 10 Similar artists links with score, contained in a <div id='SimlarArtists'>
                                Each individual result is contained in <div class="similar">.

    
Methods:
    Song(Optional string or dict)   If present, argument is passed to Song.load().

    Song.load(string or dict)       Loads Song attributes.  Value can be either a string containg the
                                    file name or a dictionary object for the song containing the following 
                                    strings: title, album, artist, file
                                    The song dict must contain at least the title OR the file (file name), 
                                    album and artist is optional but recommended.
                                    If only a file name is received, it wll be parsed for artist and title.

    Song.search()                   Runs the search and fills out the SearchResults attributes

    Song.SearchResults.parse(Optional int)  Returns a ParseResults object for the specified 
                                            SearchResults.links index.  If no result is specified,
                                            self.SearchResults.links[0] will be used.
                                            The first result is usually the correct one, but not always...

    Song.quickSearch()              Runs Song.search() and Song.SearchResults.parse() and returns a 
                                    ParseResults object for the first result found.

    parse(lyrics, album, similar)   Returns a ParseResults object for the supplied info.
                                    lyrics should be a findlyrics.com url, 
                                    album should be musicbrainz release.xml,
                                    similar should be audioscrobbler's similar.xml.
                                    Useful if you have saved links from previous searches and don't 
                                    wish to create a new Song object and repeat the search.
    

CSS that I use:
Table {
    border-collapse: collapse;
    width: 97%;
    margin-top: 5px;
    margin-left: auto;
    margin-right: auto;
    
}

TD {
    vertical-align: top;
    padding: 1px 2px 1px 2px
}
.art {
    width: 240px;
    height: 240px;
    display: table-cell;
    vertical-align: middle;
    background-color: #0A0A0A;
    border: 1px solid #222222;
}

#SimlarArtists {
    margin-top: 20px;
    padding: 10px;
    width: 220px;
    text-align: left;
    background-color: #0A0A0A;
    border: 1px solid #222222;
}
.similar {
    padding-top: 5px;
}