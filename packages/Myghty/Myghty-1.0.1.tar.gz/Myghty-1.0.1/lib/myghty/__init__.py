# $Id: __init__.py 2013 2005-12-31 03:19:39Z zzzeek $
# __init__.py 
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#


import posixpath as unixpath

# insert the "http" path into the search path for this module
__path__.insert(0, unixpath.join(__path__[0], 'http'))



