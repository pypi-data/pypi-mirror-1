from setuptools import setup, find_packages
from turbogears.finddata import find_package_data
import os
execfile(os.path.join("mpd_webamp", "release.py"))

setup(
    name="MPD-WebAMP",
    version='1.1',
    # uncomment the following lines if you fill them out in release.py
    description="""MPD WebAMP is an asynchronous web client for the Music Player Daemon""" ,
    long_description = """MPD WebAMP is a web client to control music playback on a media server PC
        from a web browser.  The program is based on TurboGears and uses it's
        own web server to interface with the Music Player Daemon, a system service
        available on GNU/Linux PCs.  MPD WebAMP provides the features and interface of a
        desktop application in a web based format.
        
        Provides the following capabilities:
        
        * Browsing of music library by folder structure.
        * Playlist manipulation, saving and loading.
        * Playback controls, volume, seek and live status display.
        * Album art, lyrics, and top ten similar artists for currently playing song.
        * Search by file name or search by tags.
        * Sessions: resume from where you left off.
        * Themes: supports theming, default theme comes in four colors.
        * Completely Asynchronous interface, no refreshing needed.

        """,
    author="cseickel",
    author_email="cseickel at gmail dot com",
    url="http://cseickel.googlepages.com/mpdwebamp",
    #download_url=download_url,
    license="GPL 2",
    
    install_requires = [
        "TurboGears >= 1.0.1",
    ],
    scripts = ["start-mpd_webamp.py"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='mpd_webamp',
                                     package='mpd_webamp'),
    keywords = [
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop
        
        # if this has widgets, uncomment the next line
        # 'turbogears.widgets',
        
        # if this has a tg-admin command, uncomment the next line
        # 'turbogears.command',
        
        # if this has identity providers, uncomment the next line
        # 'turbogears.identity.provider',
    
        # If this is a template plugin, uncomment the next line
        # 'python.templating.engines',
        
        # If this is a full application, uncomment the next line
        'mpd client', 'music', 'lyrics', 'lastfm', 'album art', 'turbogears.app',
    ],
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        'Framework :: TurboGears :: Applications',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        
        
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'nose.collector',
    entry_points = """
                   [console_scripts]
                   mpdwebamp-start = mpdwebamp.commands:start
    """
    )
    
