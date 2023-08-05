#!/usr/bin/env python2.4
#
# (c) 2007 Andreas Kostyrka
#

import sys

def parser():
    import optparse
    p = optparse.OptionParser(usage="%prog [options] [file]")
    p.add_option("--savename", "-s",
                 default=None,
                 help="prefix to save the split files to")
    return p

def splitfile(src, org, yours, theirs):
    state = (org, yours, theirs)
    for i in src:
        if i.startswith(">>>> YOUR VERSION "):
            state = (yours, )
        elif i.startswith("==== ORIGINAL VERSION "):
            state = (org, )
        elif i.startswith("==== THEIR VERSION "):
            state = (theirs, )
        elif i.startswith("<<<<"):
            state = (org, yours, theirs)
        else:
            for s in state:
                s.write(i)
            
        

def main():
    p = parser()
    opt, args = p.parse_args()
    if len(args) > 1:
        p.print_help()
        raise SystemExit(2)
    if opt.savename is None:
        opt.savename = args[0]
    if len(args) == 0:
        infile = sys.stdin
    else:
        infile = file(args[0])
    splitfile(file(args[0]),
              file(opt.savename + ".org", "w"),
              file(opt.savename + ".yours", "w"),
              file(opt.savename + ".theirs", "w"))

if __name__ == '__main__':
    main()


