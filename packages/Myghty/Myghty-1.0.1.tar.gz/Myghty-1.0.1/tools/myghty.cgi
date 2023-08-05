#!/usr/local/bin/python

# myghty cgi runner.  place in cgi-bin directory and address Myghty templates
# with URLs in the form:

# http://mysite.com/cgi-bin/myghty.cgi/path/to/template.myt

# component root.  this is where the Myghty templates are.
component_root = '/path/to/croot'

# data directory.  this is where Myghty puts its object files.
data_dir = '/path/to/datadir'

# module components.
module_components = []

# libraries.  Put paths to additional custom Python libraries here.
lib = ['/path/to/custom/libraries']

import sys
[sys.path.append(path) for path in lib]

import myghty.CGIHandler as handler

handler.handle( component_root=component_root, module_components = module_components, data_dir=data_dir)


