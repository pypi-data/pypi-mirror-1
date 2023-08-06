#!/usr/bin/env python
import Options


if __name__ == '__main__':
	sequencer = Options.get_sequencer_from_cli()
	sequencer.play()
