from gi.repository import Peas
from gi.repository import Gtk
from gi.repository import Totem
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Tracker

DISPLAY_COLUMN = 0
OBJECT_COLUMN = 1
FILENAME_COLUMN = 2

# see http://oscaf.sourceforge.net/nmm.html for descriptions of the query objects
# see http://live.gnome.org/Tracker/Documentation/Examples/SPARQL/Music for example music queries
ARTIST_QUERY = """
SELECT ?artist_name ?artist
WHERE {
    ?album a nmm:MusicAlbum; 
        nmm:albumArtist ?artist.
    ?artist nmm:artistName ?artist_name.
    # make sure the album isn't empty
    ?song nmm:musicAlbum ?album .
}  
GROUP BY ?artist
ORDER BY ?artist_name
"""

def albums_query (artist):
    artist = Tracker.sparql_escape_string(artist)
    return """
    SELECT ?album_name ?album
    WHERE {
        ?album a nmm:MusicAlbum; 
            nmm:albumArtist "%s";
            nmm:albumTitle ?album_name.
        # make sure the album isn't empty
        ?song nmm:musicAlbum ?album .
    }  
    GROUP BY ?album
    ORDER BY ?album_name
    """ % (artist, )

def songs_query (album):
    album = Tracker.sparql_escape_string(album)
    return """
    SELECT ?song_name ?song ?filename
    WHERE {
        ?song a nmm:MusicPiece; 
            nmm:musicAlbum "%s";
            nmm:trackNumber ?trackNumber;
            nie:title ?song_name ;
            nie:url ?filename ;
            nmm:musicAlbumDisc [nmm:setNumber ?disc_number].
    }  
    # need to also sort by disk number
    ORDER BY ?disc_number ?trackNumber
    """ % (album, )

class MusicLibrary(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'MusicLibrary'

    object = GObject.property(type = GObject.Object)

    def __init__(self):
        GObject.Object.__init__ (self)
        self.totem = None

    def do_activate(self):
        self.totem = self.object
        # bug, Tracker stuff should be async
        self.conn = Tracker.SparqlConnection.get (None)
        builder = Totem.plugin_load_interface ("musiclibrary", "musiclibrary.ui", True, self.totem.get_main_window (), self)
        container = builder.get_object ('root_window')

        self.music_store = builder.get_object ('music_tree_store')
        self.music_view = builder.get_object ('music_tree_view')

        container.show_all ()

        self.totem.add_sidebar_page ("musiclibrary", "Music Library", container)

        GObject.idle_add(self.populate_artists)
        self.song_clicked = self.music_view.connect("row-activated", self._song_activated_cb)

    def do_deactivate(self):
        #self.album_view.disconnect(self.album_clicked)
        #self.artist_view.disconnect(self.artist_clicked)
        self.totem.remove_sidebar_page ("musiclibrary")
        self.totem = None
        self.conn = None
        self.music_store = None
        self.music_view = None

    def populate_artists (self):
        cursor = self.conn.query (ARTIST_QUERY, None)
        while cursor.next (None):
            self.music_store.append(None, (cursor.get_string(0)[0],cursor.get_string(1)[0], None))
        GObject.idle_add(self.populate_next_album_list)
        self.next_artist_to_do_albums = self.music_store.get_iter_first()
        return False

    def populate_next_album_list (self):
        tree_model = self.music_store
        if self.next_artist_to_do_albums == None:
            self.next_artist_to_do_albums = tree_model.get_iter_first()
            self.next_album_to_do_songs = tree_model.iter_children(self.next_artist_to_do_albums)
            GObject.idle_add(self.populate_next_song_list)
            return False

        artist_object = tree_model.get_value(self.next_artist_to_do_albums, OBJECT_COLUMN)
        self.populate_album_list(artist_object, self.next_artist_to_do_albums)

        self.next_artist_to_do_albums = tree_model.iter_next(self.next_artist_to_do_albums)
        return True

    def populate_album_list (self, artist_object, artist_iter):
        cursor = self.conn.query (albums_query(artist_object), None)
        while cursor.next (None):
            self.music_store.append(artist_iter, (cursor.get_string(0)[0],cursor.get_string(1)[0], None))

    def populate_next_song_list (self):
        tree_model = self.music_store
        if self.next_artist_to_do_albums == None:
            return False
        if self.next_album_to_do_songs == None:
            self.next_artist_to_do_albums = tree_model.iter_next(self.next_artist_to_do_albums)
            self.next_album_to_do_songs = tree_model.iter_children(self.next_artist_to_do_albums)
            return True
        album_object = tree_model.get_value(self.next_album_to_do_songs, OBJECT_COLUMN)
        self.populate_song_list (album_object, self.next_album_to_do_songs)

        self.next_album_to_do_songs = tree_model.iter_next(self.next_album_to_do_songs)
        return True



    def populate_song_list (self, album_object, album_iter):
        cursor = self.conn.query (songs_query(album_object), None)
        while cursor.next (None):
            self.music_store.append(album_iter, (cursor.get_string(0)[0],cursor.get_string(1)[0],cursor.get_string(2)[0]))

    def _song_activated_cb (self, tree_view, path, view_column):
        assert tree_view == self.music_view
        tree_store = tree_view.get_model ()
        assert tree_store == self.music_store
        if path == None:
            return

        tree_iter = tree_store.get_iter (path)
        if tree_iter == None:
            return

        song_name = tree_store.get_value (tree_iter, DISPLAY_COLUMN)
        song_filename = tree_store.get_value (tree_iter, FILENAME_COLUMN)
        if song_filename:
            self.play_song(song_name, song_filename)

    def play_song(self, song_name, song_filename):
        self.totem.add_to_playlist_and_play(song_filename, song_name, True)
