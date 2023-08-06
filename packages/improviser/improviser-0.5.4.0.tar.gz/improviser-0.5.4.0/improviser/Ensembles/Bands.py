from Musicians import *

"""

	Possible instrument parameters:

		channel		=	MIDI channel
		min_velocity	=	Minimum volume [0-128]
		max_velocity	=	Maximum volume [0-128]
		chance		~= 	Chance to play on tick
		end		 = 	Iteration to end on, default: 0
		start		 = 	Iteration to start on, default: 0
		step 		=	Iterations to wait after end



"""


dummy_parameters = {'channel': 1}

dummy = [
	#SimpleChordInstrument({'channel': 1, 'start': 16}), 
	SlowStridePianist({'max_velocity': 80, 'start': 0, 'step': 2 }),
	FastStridePianist({'max_velocity': 80, 'start': 2, 'step': 2}),
	RockDrum({'start': 0}),
	#JazzDrum({'start': 8, 'end': 12}), 
	BassInstrument({'channel':1, 'start': 1}),
	ChordInstrument({'channel':7, 'chance': 0.15, \
			 'max_velocity': 70, 'start': 2}), 
	SoloInstrument({'channel':1, 'start': 4, 'end': 8, 'chance': 0.2, 
			'step': 4}),
	SoloInstrument({'channel':11, 'start': 8, 'end': 12, 'step':2}),
	SoloInstrument({'channel':12, 'start': 4, 'end': 8, 'step':4}),
	SoloInstrument({'channel':7, 'start': 16, 'end': 20, 'step': 4})
	 ]

swing = [
	ChordInstrument({'channel':7, 'chance': 0.15, 'max_velocity': 70}), 
	SlowStridePianist({'max_velocity': 80}),
	RockDrum({'start': 0}),
	SoloInstrument({'channel':11}),
	]

boogie = [
	BoogieWoogieRhythm({'channel': 1}),
	RockDrum({}),
	SoloInstrument({'channel':11}),
	]

metal = [
	BlastBeat({'max_velocity': 80}),
	PowerChords({'channel': 7}),
	SoloInstrument({'channel':11}),
	]

jazz = [
	SoloInstrument({'channel': 11}),
	ChordInstrument({'channel': 4, 'max_velocity': 70, 'chance': 0.5}),
	BassInstrument({'channel': 6}),
	SlowStridePianist({'channel': 3}),
	SimpleChordInstrument({'channel': 1}),
	RockDrum({}),
	]
