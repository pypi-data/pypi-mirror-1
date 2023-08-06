from distutils.core import setup

long_description = """\
Rupy example
============

Example on how to use PyPI.
"""

setup(name='RupyExample', version='1.0',
      author='tarek',
      author_email='tarek@ziade.org',
      url='http://example.com',
      packages=['foo', 'bar'],
      description="Rupy project",
      long_description=long_description,
      )

