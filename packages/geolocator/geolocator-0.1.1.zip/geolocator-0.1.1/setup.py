"""geolocator library: locate places and calculate distances between them

The geolocator library provides a common interface to location-related data
from various sources and provides means to calculate distances between places.
Currently the MaxMind country & city geoip data sources are supported. There is
also some preliminary support for using GNS (GEOnet Names Server )data. For
distance calculation, the Haversine function is used.

The library can be useful for example to implement location-based features in
different www frameworks; for an example of that, see the GeoLocation Zope /
CMF / Plone package from which this library was spun off. Please note, however,
that there is nothing www-specific in the library, nor does it have any
external dependencies.
"""

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Programming Language :: Python
Topic :: Scientific/Engineering :: GIS
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Libraries
Operating System :: Microsoft :: Windows
Operating System :: Unix
Operating System :: POSIX
"""

import sys
from distutils.core import setup

if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)

doclines = __doc__.split("\n")

setup(name="geolocator",
      version="0.1.1",
      maintainer="Petri Savolainen",
      maintainer_email="petri.savolainen@iki.fi",
      url = "http://geolocator.fairsay.com",
      license = "http://www.fsf.org/licensing/licenses/lgpl.txt",
      platforms = ["any"],
      packages=['geolocator','geolocator/providers','geolocator/tests'],
      description = doclines[0],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = "\n".join(doclines[2:]),
)
