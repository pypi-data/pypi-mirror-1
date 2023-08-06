from distutils.core import setup

setup(
	name="improviser",
	version="0.7.4.8",
	description="Automatic music generation software",
	long_description="Experiments in musical content generation.",
	author="Bart Spaans",
	author_email="onderstekop@gmail.com",
	url="http://www.onderstekop.nl/",
	packages = ['improviser', 'improviser.Blocks', 'improviser.Musicians',
			'improviser.Musicians.Bassists', 'improviser.Musicians.Pianists', 'improviser.Musicians.Drummers',
			'improviser.Musicians.Accompaniment', 'improviser.Musicians.Guitarists', 'improviser.Musicians.Soloists',
			'improviser.Progressions', 'improviser.Visualizations','improviser.Movements', 'improviser.qtGUI'],
	classifiers = [],
)
