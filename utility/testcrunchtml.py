import env
from htmlproc import crunchtml
import argparse
import pathlib, time

#parser = argparse.ArgumentParser(description = "Crush HTML tag stacks down to size.")
#parser.add_argument("infiles", metavar = "infile", help = "the html files to operate on", nargs = "+");
#group = parser.add_mutually_exclusive_group()
#group.add_argument("-o", "--out", default = './out', help="The output folder (default=./out)")
#group.add_argument("-m", '--modify', action = "store_true", help = "Modify source-files in-place")

#args = parser.parse_args()


inpath = pathlib.Path('./htmlproc/test')

for infile in inpath.glob('**/*.html'):
    start=time.time()
    doc = crunchtml.crunch_file(infile, xml_tags=1)
    print(time.time()-start)