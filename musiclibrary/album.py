class Album:


	def __init__(self, id, peak_gain, gain, duration, title, track_count, artist_id):
		self.id = id
		self.peak_gain = peak_gain
		self.gain = gain
		self.duration = duration
		self.title = title
		self.track_count = track_count
		self.artist_id = artist_id

	def __str__(self):
		return self.title

	def __unicode__(self):
		return self.title

	def __repr__(self):
		return self.id

	def artist(self):
		from . import artists
		return artists.Artists()[self.artist_id]

	def songs(self):
		from . import songs
		return songs.Songs().part_of_album(self.id)
