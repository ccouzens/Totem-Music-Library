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
		from . import songs
		return songs.Songs().composed_by(self.id)

	def songs_performed(self):
		from . import songs
		return songs.Songs().performed_by(self.id)

	def albums_where_album_artist(self):
		from . import albums
		return albums.Albums().where_album_artist(self.id)
