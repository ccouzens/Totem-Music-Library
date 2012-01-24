from gi.repository import Peas
from gi.repository import Gtk
from gi.repository import Totem
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Tracker

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

def sparql_safe (string):
    # is this enough?
    # what is the best way to guard against sparql injection?
    # Perhaps this? http://developer.gnome.org/libtracker-sparql/unstable/tracker-examples-builder.html
    # I can't get my head around it though.
    # 
    # bug, should be using the builder as described above
    return string.replace('"', '\\\"')

def albums_query (artist):
    artist = sparql_safe(artist)
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


#
#
#
# Handle expanding an artist
#
#
#


class MusicLibrary(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'MusicLibrary'

    object = GObject.property(type = GObject.Object)
    artist = None
    album = None
    song = None

    def __init__(self):
        GObject.Object.__init__ (self)
        self.totem = None

    def do_activate(self):
        self.totem = self.object
        # bug, Tracker stuff should be async
        self.conn = Tracker.SparqlConnection.get (None)
        builder = Totem.plugin_load_interface ("musiclibrary", "musiclibrary.ui", True, self.totem.get_main_window (), self)
        container = builder.get_object ('root_window')

        self.artist_store = builder.get_object ('artist_store')
        self.artist_view = builder.get_object ('artist_tree_view')
        self.artist_clicked = self.artist_view.connect("cursor-changed", self._artist_selected_cb)

        self.album_store = builder.get_object ('album_store')
        self.album_view = builder.get_object ('album_tree_view')
        self.album_clicked = self.album_view.connect("cursor-changed", self._album_selected_cb)

        container.show_all ()

        self.totem.add_sidebar_page ("musiclibrary", "Music Library", container)

        self.populate_artist_list ()

    def do_deactivate(self):
        self.album_view.disconnect(self.album_clicked)
        self.artist_view.disconnect(self.artist_clicked)
        self.totem.remove_sidebar_page ("musiclibrary")

    def populate_artist_list (self):
        cursor = self.conn.query (ARTIST_QUERY, None)
        while cursor.next (None):
            self.artist_store.append((cursor.get_string(0)[0][0:15],cursor.get_string(1)[0]))

    def populate_album_list (self):
        self.album_store.clear()
        cursor = self.conn.query (albums_query(self.artist), None)
        while cursor.next (None):
            self.album_store.append((cursor.get_string(0)[0],cursor.get_string(1)[0]))


    def _artist_selected_cb (self, tree_view):
        assert tree_view == self.artist_view
        tree_store = tree_view.get_model ()
        assert tree_store == self.artist_store
        (path, focus_column) = tree_view.get_cursor()

        tree_iter = tree_store.get_iter (path)
        if tree_iter == None:
            return

        self.artist = tree_store.get_value (tree_iter, 1)
        self.populate_album_list()

    def _album_selected_cb (self, tree_view):
        assert tree_view == self.album_view
        tree_store = tree_view.get_model ()
        assert tree_store == self.album_store
        (path, focus_column) = tree_view.get_cursor()
        if path == None:
            return

        tree_iter = tree_store.get_iter (path)
        if tree_iter == None:
            return

        self.album = tree_store.get_value (tree_iter, 1)
        print tree_store.get_value (tree_iter, 0)
        # self.populate_song_list()

