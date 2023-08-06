from setuptools import setup

from pywurfl import __version__, __url__, __license__
from pywurfl import __doc__ as doc


# By Armand Sat Apr 18 18:35:45 EDT 2009
# Pau Aliagas was a major contributor to this effort
# Thanks

setup (name="pywurfl",
       version=__version__,
       author=["Armand Lynch"],
       author_email=["lyncha@users.sourceforge.net"],
       contact="Armand Lynch",
       contact_email="lyncha@users.sourceforge.net",
       license=__license__,
       url=__url__,
       packages=['pywurfl'],
       scripts=['bin/wurfl2python.py'],
       description=doc,
       long_description=doc,
       platforms="All",
       classifiers=['Development Status :: 4 - Beta',
                    'Environment :: Console',
                    'Environment :: Web Environment',
                    'Intended Audience :: Developers',
                    'Intended Audience :: Telecommunications Industry',
                    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: Database :: Front-Ends',
                    'Topic :: Internet :: WAP',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                    'Topic :: Utilities'
                    ])
