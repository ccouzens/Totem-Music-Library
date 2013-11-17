from gi.repository import Tracker

class Albums:


	def __init__(self, conn=None, wheres=()):
		self.conn = conn or Tracker.SparqlConnection.get (None)
		self.wheres = wheres

	def where(self, new_condition):
		new_wheres = self.wheres + (new_condition,)
		new_association = self.__class__(self.conn, new_wheres)
		return new_association

	def sparql(self):
		return """
		SELECT
		?album
		nmm:albumPeakGain(?album)
		nmm:albumGain(?album)
		nmm:albumDuration(?album)
		nmm:albumTitle(?album)
		nmm:albumTrackCount(?album)
		nmm:albumArtist(?album)
		WHERE {
		?album a nmm:MusicAlbum.
		%s
		}
		""" % ".\n".join(self.wheres)

	def __getitem__(self, id):
		escaped_id = Tracker.sparql_escape_string(id)
		return self.where('FILTER(?album = <%s>)' % escaped_id).first()

	def first(self):
		try:
			return iter(self).next()
		except StopIteration:
			return None

	def where_album_artist(self, artist_id):
		return self.where('?album nmm:albumArtist "%s"' % Tracker.sparql_escape_string(artist_id))

	def __iter__(self):
		from . import album
		cursor = self.conn.query (self.sparql(), None)
		while cursor.next (None):
			yield album.Album(cursor.get_string(0)[0], cursor.get_string(1)[0], cursor.get_string(2)[0], cursor.get_string(3)[0], cursor.get_string(4)[0], cursor.get_string(5)[0], cursor.get_string(6)[0])

