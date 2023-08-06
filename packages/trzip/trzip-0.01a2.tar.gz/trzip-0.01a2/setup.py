from distutils.core import setup

long_description = """\
trzip.py is a quick script to stream rzip compressed files.

compress:
$ cat somefile.dat | trzip.py > somefile.trz 

decompress:
$ cat somefile.trz | trzip.py -d > somefile2.dat

Comparing result
$ cmp somefile.dat somefile2.dat
"""

setup(name='trzip', version='0.01a2', author='Clovis Fabricio',
      author_email='nosklo at gmail dot com', url='',
      maintainer='Clovis Fabricio', maintainer_email='nosklo at gmail dot com',
      description='rzip-stream library',
      long_description=long_description,
      download_url='',
      py_modules=['libtrzip'],
      scripts=['trzip'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System :: Archiving :: Compression',
          'Topic :: Utilities',
          ]
    )
