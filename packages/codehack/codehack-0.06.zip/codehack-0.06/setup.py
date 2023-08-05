from distutils.core import setup, Extension

module1 = Extension(
	'codehack.codehack_bin',
	sources = ['codehack.c']
)

settings = dict(
	name = 'codehack',
	version = '0.06',
	description = 'A tool for hacking code object of python',
	url = '',
	author = 'Nishio Hirokazu',
	author_email = 'codehack@nishiohirokazu.org',
	ext_modules = [module1],
	long_description = """
	This module include 2 features,
	one is extension (written in C) to manipulate code objects,
	and the other is utility modules work around code objects.
	Both are in alpha phase. Don't use to important project.
	""",
	packages=["codehack"],
)

if __name__ == "__main__":
	setup(**settings)
