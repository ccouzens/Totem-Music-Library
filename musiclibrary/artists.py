from gi.repository import Tracker
from copy import copy

class Artists:

	def __init__(self, conn=None):
		self.conn = conn or Tracker.SparqlConnection.get (None)
		self.wheres = ["?artist a nmm:Artist"]

	def albumArtists(self):
		return self.where("?album nmm:albumArtist ?artist")

	def songArtists(self):
		return self.where("?song nmm:performer ?artist")

	def where(self, new_condition):
		new_association = self.__clone()
		new_association.wheres.append(new_condition)
		return new_association

	def sparql(self):
		return """
		SELECT ?artist
		WHERE {
		%s.
		}
		GROUP BY ?artist
		""" % ".\n".join(self.wheres)

	def all(self):
		cursor = self.conn.query (self.sparql(), None)
		while cursor.next (None):
			yield cursor.get_string(0)[0]
		# return (cursor.get_string(0) while cursor = cursor.next (None))

	def __clone(self):
		new_association = Artists()
		new_association.wheres = copy(self.wheres)
		return new_association
