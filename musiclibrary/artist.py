import songs
import albums

class Artist:
	def __init__(self, id, name):
		self.id = id
		self.name = name

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	def __repr__(self):
		return self.id

	def songs_composed(self):
		return songs.Songs().composed_by(self.id)

	def songs_performed(self):
		return songs.Songs().performed_by(self.id)

	def albums_where_album_artist(self):
		return albums.Albums().where_album_artist(self.id)
