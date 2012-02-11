MusicLibrary Totem Plugin
=========================

A music library for [Totem](http://projects.gnome.org/totem/) that uses [Tracker](http://projects.gnome.org/tracker/) as the database.

Since it uses Tracker, it doesn't require any configuration.

In the sidebar you get a list of all the artists in your music collection.
You can drill down to their albums, then to songs.
When you double click a song, it starts playing.

![screenshot](https://github.com/ccouzens/Totem-Music-Library/raw/master/Screenshot+at+2012-02-11+21:15:35.png "screenshot")

Install
-------

    # Some of the Ubuntu dependencies:
    sudo apt-get install gir1.2-tracker-0.12 gir1.2-totem-1.0 totem tracker

    mkdir -p ~/.local/share/totem/plugins
    cd ~/.local/share/totem/plugins
    git clone git@github.com:ccouzens/Totem-Music-Library.git musiclibrary

    # start Totem
    totem

Enable the plugin and pay attention to the messages on the command line.
If you needed to install something else, let me know and I'll add to this page.
You may need to wait a while after installing Tracker before it indexes your music.

Critique
--------

I've not put much thought into how the plugin gets activated and deactivated.
It might be using more resources than it should when the it is deactivated.

When a song finishes it doesn't skip to the next one.

The code repeats itself a lot.
The code for artist, album and song is quite similiar.
