import improviser.Ensembles.Bands as Bands
import improviser.Progressions.Blues as Blues

class Block:


	progression = Blues.standard_blues
	
	bpm = 200
	iterations = 8
	resolution = 8


	instruments = Bands.swing

	def get_bpm(self, iteration):
		return self.bpm

	def get_instruments(self, iteration):
		return self.instruments

	def get_progression(self, iteration):
		p = self.progression
		res = []
		for i in range(len(p)):
			if i < len(p) - 1:
				if p[i][0] <= iteration and p[i + 1][0] > iteration:
					res= p[i][1]
					break
			else:
				res = p[i][1]
				break
		if res == 'R':
			prog = self.progression
			song_length = prog[-1][0] - prog[0][0]
			for p in prog:
				prog[prog.index(p)] = \
					(p[0] + song_length, p[1])
			return self.get_progression(iteration)
		return res


	def get_resolution(self, iteration):
		return self.resolution





