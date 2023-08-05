"""colorizer tests"""

from pudge.colorizer import Parser
import os.path as path
import os

from setupenv import *

def get_output_file(*filenames):
    file = path.join(test_output_dir, 'colorizer', *filenames)
    if not path.exists(path.dirname(file)):
        os.makedirs(path.dirname(file))
    return file

def check_xml(file):
    from xml.dom.minidom import parse
    parse(file) # parse an XML file by name

def test_colorizer():
    import os, sys, pprint
    fin = get_test_file('medium.py')
    fout = get_output_file('medium.html')
    p = Parser(fin, open(fout, 'wt'))
    p.format()
    print fout
    check_xml(fout)
    #os.system('open %s' % fout)
