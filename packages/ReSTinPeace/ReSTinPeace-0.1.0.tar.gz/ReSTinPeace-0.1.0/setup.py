from distutils.core import setup

from rip import __VERSION__

setup(
    name = 'ReSTinPeace',
    version = __VERSION__,
    description = 'A tool to make handling ReStructured Text easier.',
    author = 'P.C. Shyamshankar',
    author_email = 'sykora@lucentbeing.com',

    packages = ['rip'],

    url = 'http://github.com/sykora/rip/',
    license = 'GNU General Public License v3.0',

    classifiers = (
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Markup :: HTML',
    )
)
