from gi.repository import Tracker
from copy import copy
import artist

class Artists:

	def __init__(self, conn=None):
		self.conn = conn or Tracker.SparqlConnection.get (None)
		self.wheres = ["?artist a nmm:Artist"]

	def album_artist(self):
		return self.where("?album nmm:albumArtist ?artist")

	def song_performer(self):
		return self.where("?performedSong nmm:performer ?artist")

	def song_composer(self):
		return self.where("?composedSong nmm:composer ?artist")

	def where(self, new_condition):
		new_association = self.__clone()
		new_association.wheres.append(new_condition)
		return new_association

	def sparql(self):
		return """
		SELECT ?artist nmm:artistName(?artist)
		WHERE {
		%s.
		}
		GROUP BY ?artist
		""" % ".\n".join(self.wheres)

	def find(self, artist_id):
		escaped_artist_id = Tracker.sparql_escape_string(artist_id)
		# doesn't work
		return self.where('?artist = "%s"' % escaped_artist_id).first()

	def first(self):
		try:
			return self.all().next()
		except StopIteration:
			return None

	def all(self):
		sparql = self.sparql()
		try:
			cursor = self.conn.query (self.sparql(), None)
		except Exception, e:
			print sparql
			raise e
		while cursor.next (None):
			yield artist.Artist(cursor.get_string(0)[0], cursor.get_string(1)[0])

	def __clone(self):
		new_association = Artists()
		new_association.wheres = copy(self.wheres)
		return new_association
