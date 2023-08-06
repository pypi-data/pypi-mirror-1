class Movement:

	blocks = []
	b_counter = 0
	loop = 1
	default_bpm = 120
	default_wildness = 0.5
	default_key = 'C'
	default_resolution = 8
	swing = False

	def __init__(self):
		pass

	def add_block(self, block):
		block.key = self.default_key
		block.bpm = self.default_bpm
		block.wildness = self.default_wildness
		self.blocks.append(block)

	def set_default_bpm(self, bpm):
		self.default_bpm = bpm
	
	def set_default_wildness(self, wildness):
		self.default_wildness = wildness

	def set_default_key(self, key):
		self.default_key = key
	
	def get_next_block(self):
		"""Prepares and returns the next block in the movement.\
Returns None if there is no next block."""
		if len(self.blocks) > 0:
			if self.loop > 0:
				r = self.get_block()
				self.b_counter += 1
				if self.b_counter == len(self.blocks):
					self.b_counter = 0
					self.loop -= 1
				return r
		return None

	def get_block(self):
		return self.blocks[self.b_counter]
