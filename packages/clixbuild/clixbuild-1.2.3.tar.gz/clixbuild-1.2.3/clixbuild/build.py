#!/usr/bin/env python
import sys, os, shutil
import argparse, yaml
from clixconfig import preprocess_file

def main():
    #Step 0: Read args
    parser = argparse.ArgumentParser(description="Perform a build", prog="clixbuild", version='ClixBuild 1.2.3')
    parser.add_argument('-s', '--spec-file', action='store', metavar="BUILD_SPEC", nargs="?", default=".clixbuild", const="-", help="read BUILD_SPEC as the specfile. Omit BUILD_SPEC to use stdin")
    parser.add_argument('target', action="store", metavar="TARGET", default="default", nargs="?", help="the action to execute (default: default)")
    args = parser.parse_args()

    #Step 1: Find build file and read it.

    if args.spec_file == "-":
        #stdin!
        specfile = sys.stdin
    else:
        try:
            specfile = open(args.spec_file, 'r')
        except:
            sys.stderr.write("\nUnable to open specfile %s for reading!\n" % args.spec_file)
            sys.exit(1)

    spec = ""
    while True:
        s = specfile.read()
        if s == "": break
        spec += s

    spec = yaml.load(spec)

    if args.spec_file != "-":
        specfile.close()

    del specfile

    #Step 2: Interpret specfile directives

    def move_file(spec, f, act):
        if act[0] == 'move':
            shutil.move(f, act[1])
        else:
            shutil.copy2(f, act[1])

    action_matrix={
        'preprocess': preprocess_file,
        'move': move_file,
        'copy': move_file
    }

    for f in spec['targets'][args.target].keys():
        for act in spec['targets'][args.target][f]['actions']:
            action_matrix[act[0]](spec, f, act) #do said action

if __name__ == "__main__": main()