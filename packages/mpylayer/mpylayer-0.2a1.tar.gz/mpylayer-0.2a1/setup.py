from distutils.core import setup


long_description = """\
mpylayer is a python package to easily control mplayer in python, using a pythonic OO syntax.

A quick example:

>>> mp = mpylayer.MPlayerControl()
>>> mp.loadfile('/path/to/some_music.mp3')
>>> mp.volume = 100
"""

setup(name='mpylayer', version='0.2a1', author='Clovis Fabricio',
      author_email='nosklo at gmail dot com', url='http://code.google.com/p/mpylayer/',
      maintainer='Clovis Fabricio', maintainer_email='nosklo at gmail dot com',
      description='Pythonic mplayer controller library',
      long_description=long_description,
      download_url='http://code.google.com/p/mpylayer/downloads/list',
      packages=['mpylayer'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Multimedia :: Sound/Audio :: Players',
          'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
          'Topic :: Multimedia :: Video :: Display',
          ]
    )
