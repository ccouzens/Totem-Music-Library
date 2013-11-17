from gi.repository import Tracker
from copy import copy
import song

class Songs:

	def __init__(self, conn=None):
		self.conn = conn or Tracker.SparqlConnection.get (None)
		self.wheres = ["?song a nmm:MusicPiece"]

	def where(self, new_condition):
		new_association = self.__clone()
		new_association.wheres.append(new_condition)
		return new_association

	def composed_by(self, artist_id):
		return self.where('?song nmm:composer "%s"' % Tracker.sparql_escape_string(artist_id))

	def performed_by(self, artist_id):
		return self.where('?song nmm:performer "%s"' % Tracker.sparql_escape_string(artist_id))

	def sparql(self):
		return """
		SELECT ?song nie:title(?song) nmm:musicAlbum(?song) nmm:musicAlbumDisc(?song) nmm:performer(?song) nmm:composer(?song) nmm:trackNumber(?song) nfo:genre(?song) nie:url(?song) nfo:duration(?song)
		WHERE {
		%s.
		}
		""" % ".\n".join(self.wheres)

	def find(self, id):
		escaped_id = Tracker.sparql_escape_string(id)
		return self.where('FILTER(?song = <%s>)' % escaped_id).first()

	def first(self):
		try:
			return self.all().next()
		except StopIteration:
			return None

	def all(self):
		cursor = self.conn.query (self.sparql(), None)
		while cursor.next (None):
			yield song.Song(cursor.get_string(0)[0], cursor.get_string(1)[0], cursor.get_string(2)[0], cursor.get_string(3)[0], cursor.get_string(4)[0], cursor.get_string(5)[0], cursor.get_string(6)[0], cursor.get_string(7)[0], cursor.get_string(8)[0], cursor.get_string(9)[0])

	def __clone(self):
		new_association = Songs()
		new_association.wheres = copy(self.wheres)
		return new_association
