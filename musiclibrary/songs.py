from gi.repository import Tracker

class Songs:


	def __init__(self, conn=None, wheres=()):
		self.conn = conn or Tracker.SparqlConnection.get (None)
		self.wheres = wheres

	def where(self, new_condition):
		new_wheres = self.wheres + (new_condition,)
		new_association = self.__class__(self.conn, new_wheres)
		return new_association

	def composed_by(self, artist_id):
		return self.where('?song nmm:composer "%s"' % Tracker.sparql_escape_string(artist_id))

	def performed_by(self, artist_id):
		return self.where('?song nmm:performer "%s"' % Tracker.sparql_escape_string(artist_id))

	def part_of_album(self, album_id):
		return self.where('?song nmm:musicAlbum "%s"' % Tracker.sparql_escape_string(album_id))

	def sparql(self):
		return """
		SELECT ?song nie:title(?song) nmm:musicAlbum(?song) nmm:musicAlbumDisc(?song) nmm:performer(?song) nmm:composer(?song) nmm:trackNumber(?song) nfo:genre(?song) nie:url(?song) nfo:duration(?song)
		WHERE {
		?song a nmm:MusicPiece.
		%s
		}
		""" % ".\n".join(self.wheres)

	def __getitem__(self, id):
		escaped_id = Tracker.sparql_escape_string(id)
		return self.where('FILTER(?song = <%s>)' % escaped_id).first()

	def first(self):
		try:
			return iter(self).next()
		except StopIteration:
			return None

	def __iter__(self):
		from . import song
		cursor = self.conn.query (self.sparql(), None)
		while cursor.next (None):
			yield song.Song(cursor.get_string(0)[0], cursor.get_string(1)[0], cursor.get_string(2)[0], cursor.get_string(3)[0], cursor.get_string(4)[0], cursor.get_string(5)[0], cursor.get_string(6)[0], cursor.get_string(7)[0], cursor.get_string(8)[0], cursor.get_string(9)[0])

