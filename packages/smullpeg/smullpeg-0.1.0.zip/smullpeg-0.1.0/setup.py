from distutils.core import setup

setup(name="smullpeg",
      version='0.1.0',
      description="a lamentable peg game",
      author="Jacob Smullyan",
      author_email="smulloni@smullyan.org",
      classifiers=['Topic :: Games/Entertainment :: Puzzle Games'],
      license="GPL",
      packages=["pegs"],
      package_data={'pegs' : ['book.db', 'sounds/*.ogg']},
      scripts=['smullpeg'])
