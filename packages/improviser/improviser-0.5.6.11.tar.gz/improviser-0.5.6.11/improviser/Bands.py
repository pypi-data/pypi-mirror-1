from Musicians import *
from random import randrange

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
	SoloInstrument({'channel':11, 'midi_instr': 66, 'start': 0, 'step': 4}),
	SoloInstrument({'channel':12, 'midi_instr': 11, 'start': 4, 'step': 4}),
	BassInstrument({'channel':5, 'midi_instr':36, 'let_ring': True}),
	SimpleChordInstrument({'channel': 1, 'start': 1, 'midi_instr': 49, 'step': 1}), 
	]

weird = [
	SlowStridePianist({'channel': 1, 'start': 4}),
	ChromaticSoloist({'channel': 2, 'midi_instr': 108, 'start': 0, 'step': 4}),
	ChromaticSoloist({'channel': 3, 'midi_instr': 30, 'start': 2, 'end': 8, 'step': 2}),
	BassInstrument({'channel':4, 'midi_instr':36, 'let_ring': True, 'start': 6}),
	SoloInstrument({'channel':5, 'midi_instr':41, 'start': 6, 'end': 8, 'step': 6}),
	ChordInstrument({'channel':6, 'chance': 0.25, 'max_velocity': 70, 'midi_instr': 10, 'start': 0, 'step': 4}), 
	RockDrum({'start': 8, 'step': 8}),
	JazzDrum({'start': 0, 'step': 8}),
	]

soothing = [
	SoloInstrument({'channel': 3, 'midi_instr': 25, 'start': 4, 'end': 8, 'step': 4}),
	WalkingBass({'channel':4, 'midi_instr':35, 'let_ring': True, 'start': 0}),
	ChordInstrument({'channel':5, 'chance': 0.25, 'max_velocity': 70, 'midi_instr': 6, 'start': 0, 'step': 4}), 
	ChromaticSoloist({'channel': 6, 'midi_instr': 21, 'start': 8, 'end': 12, 'step': 4}),
	PowerChords({'channel': 7, 'midi_instr': 30, 'start': 8, 'end': 12, 'step': 4}),
	FastStridePianist({'channel': 8, 'midi_instr': 1, 'max_velocity': 80, 'start': 20, 'step': 4}),
	RockDrum({'start': 4}),
	
	]

none = []

boogie = [
	BoogieWoogieRhythm({'channel': 1, 'midi_instr': randrange(25, 31)}),
	BoogieWoogieRhythm({'channel': 2, 'midi_instr': randrange(1, 10)}),
	RockDrum({}),
	SoloInstrument({'channel':11, 'midi_instr': randrange(25, 90)}),
	BassInstrument({'channel':5, 'midi_instr':36, 'let_ring': True}),
	]

rocknroll= [
	BoogieWoogieRhythm({'channel': 1, 'midi_instr': 29, 'start':2, 'step': 2}),
	BoogieWoogieRhythm({'channel': 3, 'midi_instr': 30, 'start': 4, 'step': 2}),
	BoogieWoogieRhythm({'channel': 2, 'midi_instr': 4, 'start': 0}),
	RockDrum({}),
	SoloInstrument({'channel':11, 'midi_instr': 30}),
	BassInstrument({'channel':5, 'midi_instr':36, 'let_ring': True}),
	Strings({'channel': 6, 'start': 4, 'midi_instr': 49, 'step': 4, 'let_ring': True}), 
	]

metal = [
	BlastBeat({'max_velocity': 80}),
	PowerChords({'channel': 7, 'midi_instr': 30}),
	ChromaticSoloist({'channel':6, 'midi_instr': 29, 'max_velocity':80, 'start': 0, 'step':4}),
	ChromaticSoloist({'channel':8, 'midi_instr': 28, 'max_velocity':80, 'start': 4, 'step':4}),
	BassInstrument({'channel':5, 'midi_instr':36}),
	Strings({'channel': 1, 'start': 4, 'midi_instr': 49, 'step': 4, 'let_ring': True}), 
	Strings({'channel': 1, 'start': 8, 'midi_instr': 30, 'step': 4, 'let_ring': True}), 
	]

jazz = [
	SimpleChordInstrument({'channel': 1}),
	BassInstrument({'channel': 2, 'start': 0, 'let_ring': True}),
	SlowStridePianist({'channel': 3, 'start':0, 'step': 4, 'max_velocity': 70}),
	ChordInstrument({'channel': 4, 'max_velocity': 70, 'chance': 0.5, 'start': 4, 'midi_instr': 1}),
	FastStridePianist({'channel': 5, 'start':4, 'step': 4}),
	RockDrum({}),
	SoloInstrument({'midi_instr': 11, 'channel': 11, 'start': 0, 'step': 4}),
	SoloInstrument({'midi_instr': 66,'channel': 15, 'start': 4, 'stop': 8, 'step': 4, 'max_velocity': 80}),
	]

jazz2 = [
	ChromaticSoloist({'channel': 0, 'midi_instr': randrange(20,100)}),
	FastStridePianist({'channel': 5, 'start':0}),

	]
