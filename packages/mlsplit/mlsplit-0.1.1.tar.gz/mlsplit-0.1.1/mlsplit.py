#!/usr/bin/env python
"""mlsplit - Split Malayalam words into letters

This script splits Malayalam words into letters.
Ref: http://tinyurl.com/3v729s

Usage:

  python mlsplit.py input.txt [input.txt-out.txt]


Copyright (C) 2008 Baiju M <baiju.m.mail AT gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import codecs

signs = [
    u'\u0d02', u'\u0d03', u'\u0d3e', u'\u0d3f', u'\u0d40', u'\u0d41',
    u'\u0d42', u'\u0d43', u'\u0d44', u'\u0d46', u'\u0d47', u'\u0d48',
    u'\u0d4a', u'\u0d4b', u'\u0d4c', u'\u0d4d']

chandrakkala = u'\u0d4d'

def split_chars(input_file):
    text = codecs.open(input_file, 'r', 'utf-8').read()
    lst_chars = []
    for char in text:
        if char in signs:
            lst_chars[-1] = lst_chars[-1] + char
        else:
            try:
                if lst_chars[-1][-1] == chandrakkala:
                    lst_chars[-1] = lst_chars[-1] + char
                else:
                    lst_chars.append(char)
            except IndexError:
                lst_chars.append(char)

    return lst_chars

def write_output(lst_chars, output_file, separator='\t'):
    output = open(output_file, 'w')

    for char in lst_chars:
        output.write(char.encode('utf-8'))
        output.write(separator)

    output.close()

def main():
    try:
        input_file = sys.argv[1]
    except IndexError:
        print "Usage: python mlsplit.py input.txt [input.txt-out.txt]"
        sys.exit(1)
    try:
        output_file = sys.argv[2]
    except IndexError:
        output_file = input_file+'-out.txt'
    lst_chars = split_chars(input_file)
    write_output(lst_chars, output_file)

if __name__ == '__main__':
    main()
