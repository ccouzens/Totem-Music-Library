from gi.repository import Peas
from gi.repository import Gtk
from gi.repository import Totem
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Tracker

ALBUM_QUERY = """
SELECT ?artist ?artist_name
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


class MusicLibrary(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'MusicLibrary'

    object = GObject.property(type = GObject.Object)

    def __init__(self):
        GObject.Object.__init__ (self)
        self.totem = None

    def do_activate(self):
        self.totem = self.object
        self.conn = Tracker.SparqlConnection.get (None)
        builder = Totem.plugin_load_interface ("musiclibrary", "musiclibrary.ui", True, self.totem.get_main_window (), self)
        container = builder.get_object ('root_window')

        self.library_tree_store = builder.get_object ('library_tree_store')
        container.show_all ()

        self.totem.add_sidebar_page ("musiclibrary", "Music Library", container)

        self.populate_album_list ()

    def do_deactivate(self):
        self.totem.remove_sidebar_page ("musiclibrary")

    def populate_album_list (self):
        cursor = self.conn.query (ALBUM_QUERY, None)
        while cursor.next (None):
            self.library_tree_store.append(None, (cursor.get_string(1)[0],))
