from distutils.core import setup

setup(name='mpylayer', version='0.1a', author='Clovis Fabricio',
      author_email='nosklo at gmail dot com', url='http://none.for.now',
      packages=['mpylayer'],
      package_data={'mpylayer': ['data/properties.pickle']},
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
