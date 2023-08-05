Sorta topheavy with requirements :(

This plugin and some test programs require pyproj.

This can be accomplished by three routes:

1. Standard package for your Linux system

2. Downloading and installing PROJ.4 from source

3. Downloading and installing pyproj from source

4. Installing pygrib (grib2.grib2)

The test data is not put on the SVN repository due to its
size.   Please download from:

http://ak.aoos.org/data/tmp/ncep/

If the data is not found, email Rob Cermak
  cermak -> sfos.uaf.edu

The plugin also requires the python module BeautifulSoup.
This might be a standard package on your linux system.

MORE NOTES:

1. For gdalinfo to stop complaining about a non DODS/DAP 3.1, you have
to bump the version of the Paster server from 0.5 to 3.1.

2. To run the gdal_test, you need to have proj4 and gdal installed.

SOURCES:

BeautifulSoup : http://www.crummy.com/software/BeautifulSoup/

PROJ.4 : http://proj.maptools.org/

pyproj : http://python.org/pypi/pyproj

GDAL   : http://www.gdal.org/

pyGRIB      : http://www.cdc.noaa.gov/people/jeffrey.s.whitaker/python/grib2/
grib2.grib2

    It is recommended, but it should be *required* that you have the
    Jasper, PNG and zlib libraries installed.
