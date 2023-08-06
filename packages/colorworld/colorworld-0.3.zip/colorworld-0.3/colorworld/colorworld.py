"""
Make a world map from some data.
"""
from __future__ import with_statement

import colorsys
import csv
from lxml.etree import Element, parse
import re
import sys
from math import ceil, log10, floor
from optparse import OptionParser, NO_DEFAULT
import os.path
import textwrap
from textwrap import wrap

from country import convert_country_full_name_to_name


ns = {'svg': "http://www.w3.org/2000/svg"}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def listify(gen):
    "Convert a generator into a function which returns a list."
    def patched(*args, **kwargs):
        return list(gen(*args, **kwargs))
    return patched


def _build_parser():
    def clever_wrap(string):
        return re.sub(" +", " ", "\n".join(wrap(string.strip())))

    DESCRIPTION = clever_wrap("""
    Produce an svg world-map showing numerical data for countries by shading each according 
    to its numerical value. The input file must be a CSV file consisting
    of ISO 2 letter country codes and their values. If no input 
    file is given standard in is used.

    This list does not need to be complete.""")

    USAGE = "%%prog [options] [CSVFILE]\n\n%s" % DESCRIPTION

    Parser = OptionParser(usage=USAGE)
    Parser.add_option("-H", "--hue", type="int", default=120,
                      help="specify the hue for the color-scheme (between 0 and 360)")
    Parser.add_option("-o", "--output", default="", metavar="FILE",
                      help="output map to FILE. (default is an svg-file corresponding to the input file or output.svg)")
    Parser.add_option("-d", "--divisions", default=5, type="int", metavar="DIVISIONS",
                      help="Number of shades to use when color-coding")
    Parser.add_option("-u", "--unit", default="kg", metavar="UNIT",
                      help="Symbol which should be used for units")
    Parser.add_option("-m", "--multiplier", default=0, type="int", metavar="EXPONENT",
                      help="Scale values down by a power of ten")
    Parser.add_option("-l", "--long-names", action="store_true",
                      help="data uses long (english) country names instead of ISO codes. Try to interpret these.")
    return Parser

Parser = _build_parser()


@listify
def _get_option_docs():
    for option in Parser.option_list:
        name = option.get_opt_string()[2:].replace('-', '_')
        default = None if option.default == NO_DEFAULT else option.default 
        if name == "help":
            continue
        description = option.help
        INDENT = 5
        lines = wrap(" " * INDENT + "* %s: %s (default %r)" % (name, description, default))
        yiel =  lines[0] + '\n' +  '\n'.join(" " * (INDENT + 4) + line 
            for line in wrap("\n".join(lines[1:]), width=60))
        yield yiel


MAKE_MAP_DOC = """Make a colored world map for some data.

    target should be the path to an output file.

    stream_file_or_dict must be one of
     * The path to a csv of two-letter-country-codes and numeric values
     * A stream containing such values
     * A dictionary mapping two-letter-country-codes to numerical values

    These two letter country codes are those specified by ISO 3166.

    The keyword args which can be given are:\n%s""" % '\n'.join(_get_option_docs())

def make_map(stream_file_or_dict, target, **kwargs):
    
    if isinstance(stream_file_or_dict, str):
        stream = file(stream_file_or_dict, 'r')
    else:
        stream = stream_file_or_dict
        
    options = Options(output=target, **kwargs)
    return make_map_with_options(stream, options) 
make_map.__doc__ = MAKE_MAP_DOC
    

def make_map_with_options(stream, options):
    tree = parse(file(os.path.join(BASE_DIR, 'world-template.svg')))

    if hasattr(stream, 'read'):
        countries, data = _get_data(stream, options)
    else:
        for key, value in stream.items():
            if value < 0:
                del stream[key]
        countries, data = stream.keys(), stream.values()
        countries = map(str.lower, countries)

    big = max(data)
    division_size = find_nice_division(big, options.divisions)
    for country, datum in zip(countries, data):
        color = _convert_to_color_division(datum, division_size, options)
        for el in tree.xpath('//*[@id="%s"]/descendant-or-self::*' % country):
            el.attrib['style'] = 'fill:%s;fill-opacity:1;stroke:black; stroke-width:1;' % color
    
        
    x_0, y_0 = 100, 710
    width = 100
    height = 500 // options.divisions
    
    y = y_0
    for i in reversed(range(options.divisions)):
        y += height
        color_box = Element('{http://www.w3.org/2000/svg}rect', x=str(x_0), 
                            y=str(y),
                            height=str(height), 
                            width=str(width))
        color_box.attrib['style'] = 'fill:%s; fill-opacity:1;' % _convert_to_color_division(i, 1.0, options)
        label = Element('{http://www.w3.org/2000/svg}text', 
                        x=str(x_0 + width + 10),
                        y=str(y + height // 2))
        label.text = "More than %s %s" % (str(float(i * division_size) / 10**options.multiplier), options.unit)
        tree.getroot().append(color_box)
        tree.getroot().append(label)
        
    tree.write(options.output)


def find_nice_division(maximum, divisions):
    """
    Find a nice way to split the interval [0, maximum] into the given number of divisions.
    """
    big = float(maximum) / (divisions - 1)
    small = float(maximum) / divisions
    b = floor(log10(big))

    while not open_interval_contains_integer(small/ 10**b, big/ 10**b):
        b -= 1
    k = largest_integer_below(big / 10**b)

    return k*10**b


def open_interval_contains_integer(small, big):
    if floor(small) == small:
        small += 0.5
    if ceil(big) == big:
        big -= 0.5
    return ceil(small) < big


def largest_integer_below(x):
    if floor(x) == x:
        return floor(x) - 1
    return floor(x)


LIGHTEST = 0.9
def _convert_to_color_division(datum, division_size, options):
    datum = floor(datum / division_size + 1) / options.divisions
    rgb = tuple(int(c * 255) for c in colorsys.hls_to_rgb(options.hue, LIGHTEST - datum * 0.75, 0.5))
    return "#%02x%02x%02x" % rgb


def is_line_interesting(line):
    if not line.strip():
        return False
    if line.strip().startswith('#'):
        return False
    return True
        

def _get_data(stream, options):
    data = []
    countries = []
    with stream:
        for record in csv.reader(filter(is_line_interesting, stream)):
            country = record[0].lower().strip()
            if options.long_names:
                try:
                    country = convert_country_full_name_to_name(country).lower()
                except KeyError:
                    continue

            datum = float(record[1].strip())
            if datum < 0:
                continue

            countries.append(country)
            data.append(datum)
        return countries, data


def dictify(func):
    def patched(*args, **kwargs):
        return dict(func(*args, **kwargs))
    return patched
    

@dictify
def get_options():
    for option in Parser.option_list:
        name = option.get_opt_string()[2:].replace('-', '_')
        if option.default == NO_DEFAULT:
            default = None
        else:
            default = option.default
        yield name, default

OPTIONS = get_options()

class Options(object):
    def __init__(self, **kwargs):
        if not set(kwargs) <= set(OPTIONS):
            raise TypeError("These options are unknown: %r" % 
                set(OPTIONS) - set(kwargs))

        for name, default in dict(OPTIONS, **kwargs).items():
            setattr(self, name, default)

        self.hue = float(self.hue) / 360


def main():
    "Main for executable script."
    options, args = Parser.parse_args()
    if len(args) == 0:
        input = ""
    elif len(args) == 1:
        input = args[0]
    else:
        print parser.usage
        sys.exit(1)

    if not options.output:
        if input:
            base, _ = os.path.splitext(input)
            options.output = base + '.svg'
        else:
            options.output = sys.stdout

    options.hue = float(options.hue) / 360

    stream = file(input) if args else sys.stdin
    make_map_with_options(stream, options)


