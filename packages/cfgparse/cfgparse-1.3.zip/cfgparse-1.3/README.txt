cfgparse --- python configuration file parser module
Author: Dan Gass (dan.gass@gmail.com)
Download Source and Documentation: https://sourceforge.net/projects/cfgparse
Requires: Python 2.3 -or- Python 2.2 and textwrap module from 2.3

Installation:
-------------
Type "python setup.py install" and cfgparse.py will automatically be installed
in a location where it should be able to be imported.  If you do not have write
privledges type, "python setup.py install --home=/home/name" (modifying 
/home/name to your desired location) and make sure cfgparse.py is in your Python 
module search path (you can set up the PYTHONPATH environment variable to 
include the path).  Alternatively you can just copy cfgparse.py somewhere into
your module search path.


V1.2 (April 30, 2005)
---------------------------------------------------------------------------------------

Minor changes (no functional changes):
1) setup.py installation script included in distribution
2) distribution checked into CVS and built from it
3) section 2.5 title changed to include "and Obtaining Options" to help make it more
   obvious where to look on how to retrieve configuration file options.


V1.1 (March 21, 2005)
---------------------------------------------------------------------------------------

Minor functionality changes:
1) added exception argument to ConfigParser initializer to specify the exception
   class to be used to raise an exception when a user error is encountered (argument
   defaults to causing sys.exit() to be called otherwise).
2) improved error information reported when user errors are encountered.


V1.0 (January 30, 2005)
---------------------------------------------------------------------------------------
First publicly announced release

Minor functionality changes:
1) duplicate destinations are now allowd (no longer raise exception)
2) cooperating command line and configuration file parser options are now
   tolerant of incompatibilities (no longer raise exceptions)
3) INI file write() method requires a file object (previously defaulted to sys.stdout)
4) error messages improved, now gives file name (and line numbers for INI files).
5) 'tex' doctest no longer requires Python2.4


V0.00 (January 17, 2005)
---------------------------------------------------------------------------------------
initial release (unannounced)



