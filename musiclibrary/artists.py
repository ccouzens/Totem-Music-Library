from gi.repository import Tracker

class Artists:


	def __init__(self, conn=None, wheres=()):
		self.conn = conn or Tracker.SparqlConnection.get (None)
		self.wheres = wheres

	def album_artists(self):
		return self.where("?album nmm:albumArtist ?artist")

	def song_performers(self):
		return self.where("?performedSong nmm:performer ?artist")

	def song_composers(self):
		return self.where("?composedSong nmm:composer ?artist")

	def where(self, new_condition):
		new_wheres = self.wheres + (new_condition,)
		new_association = self.__class__(self.conn, new_wheres)
		return new_association

	def sparql(self):
		return """
		SELECT ?artist nmm:artistName(?artist)
		WHERE {
		?artist a nmm:Artist.
		%s
		}
		GROUP BY ?artist
		""" % ".\n".join(self.wheres)

	def __getitem__(self, id):
		escaped_id = Tracker.sparql_escape_string(id)
		return self.where('FILTER(?artist = <%s>)' % escaped_id).first()

	def first(self):
		try:
			return iter(self).next()
		except StopIteration:
			return None

	def __iter__(self):
		from . import artist
		cursor = self.conn.query (self.sparql(), None)
		while cursor.next (None):
			yield artist.Artist(cursor.get_string(0)[0], cursor.get_string(1)[0])
