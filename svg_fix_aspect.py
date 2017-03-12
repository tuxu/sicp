#!/usr/bin/env python3
"""Replace width and height of an SVG with the values specified in the viewbox.
"""
import sys
import re
from lxml import etree

def process_file(filename):
    print('\nProcessing {}'.format(filename))
    tree = etree.parse(filename)
    root = tree.getroot()
    old_width = root.attrib.get('width')
    old_height = root.attrib.get('height')
    print('Before: width="{}" height="{}"'.format(old_width, old_height))
    try:
        viewbox = root.attrib['viewBox'].split(' ')
    except KeyError:
        print('No viewBox found. Doing nothing.')
        return
    width, height = viewbox[2], viewbox[3]
    root.attrib['width'] = width
    root.attrib['height'] = height
    print('After: width="{}" height="{}"'.format(root.attrib['width'],
                                                 root.attrib['height']))
    with open(filename, 'wb') as f:
        s = etree.tostring(tree, encoding='UTF-8', xml_declaration=True,
                           pretty_print=True)
        f.write(s)

if __name__ == '__main__':
    arguments = sys.argv[1:]
    for filename in arguments:
        process_file(filename)
