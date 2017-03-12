#!/usr/bin/env python3
import sys
import re
import json
import html
import subprocess
from latex2svg import latex2svg

formula_re = re.compile(r"\\\([\s\S]+?\\\)|\\\[[\s\S]+?\\\]")


def find_equations(filename):
    with open(filename, 'r') as f:
        contents = f.read()
    return formula_re.findall(contents, re.MULTILINE)


def process_equation(equation_html):
    # Fix LaTeX
    latex = html.unescape(equation_html)
    latex = re.sub(r'\n\s*?\n', '\n', latex, flags=re.MULTILINE)
    latex = latex.replace(r'\lt', '<').replace(r'\gt', '>')
    if 'eqnarray' in latex:
        latex = latex[2:-2].strip()
    if 'eqalign' in latex:
        latex = (r'\begin{align*}' + '\n'.join(latex.split('\n')[2:-1]) +
                 r'\end{align*}')
    if r'\matrix' in latex:  # very fragile!
        latex = latex.replace(r'}', r'\end{matrix}') \
                     .replace(r'\matrix{', r'\begin{matrix}')

    # Render SVG
    try:
        svg = latex2svg(latex)
    except subprocess.CalledProcessError as exc:
        raise exc

    style = ''
    if svg['height'] is not None:
        style += 'height: {:.3f}em;'.format(svg['height'])
    if svg['depth'] is not None and svg['depth'] != 0:
        style += ' vertical-align: {:.3f}em;'.format(-svg['depth'])

    return {'code': svg['svg'], 'style': style}


if __name__ == '__main__':
    db_filename = sys.argv[1]
    html_files = sys.argv[2:]

    equations = set()
    for filename in html_files:
        equations = equations.union(set(find_equations(filename)))
    print('Processing {} equations.'.format(len(equations)))

    try:
        with open(db_filename, 'r') as f:
            database = json.load(f)
    except IOError:
        database = {}

    for i, key in enumerate(equations):
        print('\r{:03d} / {:03d}'.format(i+1, len(equations)), end='')
        if key in database:
            continue
        try:
            database[key] = process_equation(key)
        except subprocess.CalledProcessError as exc:
            print(' Processing error!')

    with open(db_filename, 'w') as f:
        json.dump(database, f)
    