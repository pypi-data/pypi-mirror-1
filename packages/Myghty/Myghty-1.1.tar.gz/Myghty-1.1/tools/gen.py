#!/usr/bin/env python

import sys

try:
    import optparse
except:
    sys.stderr.write("gen.py requires the optparse module, available in python 2.3 or higher\n")
    sys.exit(-1)

import myghty.interp
import StringIO, re, os.path

parser = optparse.OptionParser(usage = "usage: %prog [options] files...")
parser.add_option("--croot", action="store", dest="component_root", default=".", help="set component root (default: ./)")
parser.add_option("--dest", action="store", dest="destination", default=".", help="set destination directory (default: ./)")
parser.add_option("--stdout", action="store_true", dest="stdout",  help="send output to stdout")
parser.add_option("--datadir", action="store", dest="datadir", help="set data directory (default: dont use data directory)")
parser.add_option("--ext", action="store", dest="extension", default=".html", help="file extension for output files (default: .html)")
parser.add_option("--source", action="store_true", dest="source", help="generate the source component to stdout")

(options, args) = parser.parse_args()


params = {}
if options.datadir:
    params['data_dir'] = options.datadir

interp = myghty.interp.Interpreter(component_root = options.component_root,
                **params
                )

if not len(args):
    parser.print_help()

for arg in args:
    
    if options.source:
        source = interp.resolver.get_component_source(arg)
        source.get_object_code(interp.compiler(), sys.stdout)
        continue

    elif options.stdout:
        outbuf = sys.__stdout__
    else:
        (dir, name) = os.path.split(arg)
        if options.destination:
            dir = options.destination
            
        outfile = re.sub(r"\..+$", "%s" % options.extension, name)
        outfile = os.path.join(dir, outfile)
        print "%s -> %s" % (arg, outfile)
        outbuf = open(outfile, "w")
        

    interp.execute(arg, out_buffer = outbuf)
    
    if not options.stdout:
        outbuf.close()


    




