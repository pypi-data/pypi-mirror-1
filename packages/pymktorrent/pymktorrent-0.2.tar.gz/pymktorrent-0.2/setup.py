from distutils.core import setup

setup(
    name='pymktorrent',
    version='0.2',
    description='Torrent creation utility',
    author='Ludvig Ericson',
    author_email='ludvig.ericson@gmail.com',
    url='http://labs.lericson.se/experiments/pymktorrent/',
    packages=['pymktorrent'],
    scripts=['pymktorrent/maketorrent.py'],
)
