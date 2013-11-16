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
