import artists

class Song:
	def __init__(self, id, title, album_id, album_disc_id, performer_id, composer_id, track_number, genre, url, duration):
		self.id = id
		self.title = title
		self.album_id = album_id
		self.performer_id = performer_id
		self.composer_id = composer_id
		self.track_number = track_number
		self.genre = genre
		self.url = url
		self.duration = duration

	def __str__(self):
		return self.title

	def __unicode__(self):
		return self.title

	def __repr__(self):
		return self.id

	def performer(self):
		return artists.Artists().find(self.performer_id)

	def composer(self):
		return artists.Artists().find(self.composer_id)
