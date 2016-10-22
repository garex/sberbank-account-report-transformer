#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, sys
import signal
import locale
from datetime import datetime

def main():
    start_output()
    args = parse_args()
    table = parse_table(args.file)
    table = horizontal_squash(table)
    table = vertical_squash(table)
    table = expand_description(table)
    table = strip_spaces(table)
    table = parse_dates(table)
    output_table(table)
    finish_output()

def parse_args():
    parser = argparse.ArgumentParser(description='Transforms Sberbank`s card account report from fixed-width pages to single tab-delimeted table.')
    parser.add_argument('file', default='-', nargs='?', type=argparse.FileType('r'), help='File with statement')
    return parser.parse_args()

def parse_table(file):
    table = []
    delimeter_counter = 0
    is_parse = False
    for line in file:
        line = line.decode('cp1251').encode('utf8').rstrip('\r\n')
        if line.startswith('--------------------'):
            delimeter_counter += 1
            if delimeter_counter == 3:
                delimeter_counter = 0
            is_parse = (delimeter_counter == 2)
            continue

        if not is_parse:
            continue

        if '*****************' in line:
            continue

        cells = fixed_slices(line, 20, 6, 7, 8, 22, 4, 17, 17)
        table.append(cells)

    return table

def fixed_slices(string, *widths):
    position = 0
    parts = []
    for length in widths:
        part = string.decode('utf-8')[position:position + length]
        parts.append(part)
        position += length
    return parts

def horizontal_squash(table):
    out = []
    for row in table:
        out.append(row[1:])
    return out

def vertical_squash(table):
    out = []
    for row in table:
        if row[0].strip() == '':
            out[-1] = merge_rows(out[-1], row)
        else:
            out.append(row)
    return out

def merge_rows(top, bottom):
    out = []
    for i, cell in enumerate(bottom):
        out.append(top[i])
        if cell.strip():
            out[i] += '' + cell
    return out

def expand_description(table):
    out = []
    for row in table:
        expanded = row[:]
        cells = fixed_slices(expanded[3].encode('utf-8'), 25, 14, 2, 50)
        expanded[3] = cells[0]
        del cells[0]
        expanded += cells
        out.append(expanded)
    return out

def strip_spaces(table):
    out = []
    for row in table:
        out.append([cell.strip() for cell in row])
    return out

def parse_dates(table):
    try:
        locale.setlocale(locale.LC_ALL, 'ru_RU.utf-8')
    except:
        return table

    out = []
    for original_row in table:
        row = original_row[:]
        row[0] = parse_date(row[0].lower().encode('utf-8'), '%d%b')
        row[1] = parse_date(row[1].lower().encode('utf-8'), '%d%b%y')
        out.append(row)
    return out

def parse_date(string, format):
    try:
        date = datetime.strptime(string, format)
        if date.year == 1900 :
            date = date.replace(year = datetime.now().year)
        return date.strftime('%Y-%m-%d')
    except:
        return string

def output_table(table):
    for row in table:
        print '\t'.join(row)

def start_output():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def finish_output():
    sys.stdout.flush()

if __name__ == '__main__': main()
