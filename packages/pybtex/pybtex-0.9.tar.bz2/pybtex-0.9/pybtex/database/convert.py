# Copyright (C) 2006, 2007, 2008  Andrey Golovizin
#
# This file is part of pybtex.
#
# pybtex is free software; you can redistribute it and/or modify
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# pybtex is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybtex; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

"""convert bibliography database from one format to another
"""
from os import path
from pybtex.plugin import find_plugin
from pybtex.database.formats import format_for_extension

class ConvertError(Exception):
    pass

def format_for_filename(filename):
    ext = path.splitext(filename)[1].lstrip(path.extsep)
    return format_for_extension[ext]

def convert(input, output,
        from_format=None, to_format=None,
        input_encoding=None, output_encoding=None,
        parser_options=None):
    if parser_options is None:
        parser_options = {}
    if from_format is None:
        from_format = format_for_filename(input)
    if to_format is None:
        to_format = format_for_filename(output)
    input_format = find_plugin('database.input', from_format)
    output_format = find_plugin('database.output', to_format)
    
    if input == output:
        raise ConvertError('input and output file can not be the same')

    bib_data = input_format.Parser(input_encoding, **parser_options).parse_file(input)
    output_format.Writer(output_encoding).write_file(bib_data, output)
