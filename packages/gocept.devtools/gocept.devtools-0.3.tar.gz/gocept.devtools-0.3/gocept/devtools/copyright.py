#!/usr/bin/env python2.5
# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import datetime
import optparse
import os.path
import re
import sys


def fix_file(file, owner, year, append):
    output = StringIO.StringIO()
    for number, line in enumerate(file):
        if line.endswith('\n'):
            line = line[:-1]
            trail = '\n'
        else:
            trail = ''
        if append:
            line, has_copyright = fix_line(line)
            if has_copyright:
                line = line + '\n' + fix_line(
                    line, owner, year, replace_years=True)[0]
        else:
            line, _ = fix_line(line, owner, year)
        line = line + trail
        output.write(line)
    return output


def fix_line(line, owner=None, year=None, replace_years=False):
    TEMPLATE_PATTERN = re.compile(
        '^(?P<lead>.*)Copyright \\(c\\) '
        '(?P<periods>[0-9\-, ]+) (?P<owner>.*)$')
    m = TEMPLATE_PATTERN.match(line)
    # This doesn't look like a copyright line at all. Just leave as is.
    if m is None:
        return line, False

    lead = m.group('lead')
    if lead.strip() == '#':
        # Python copyright line
        pass
    elif lead.strip() == '':
        # C copyright line, embedded in multi-line comment
        pass
    else:
        raise ValueError('Invalid lead for copyright line', line)

    years = set()
    periods = m.group('periods').split(',')

    for period in periods:
        period = period.replace(' ', '')
        if '-' not in period:
            # A single year period
            years.add(int(period))
            continue
        if period.count('-') > 1:
            # Something is wrong, stop processing.
            return line, False
        # A multi-year period
        first, last = period.split('-')
        years.update(range(int(first), int(last) + 1))

    if year is not None:
        years.add(year)
    years = sorted(years)

    if replace_years:
        if year is None:
            year = years[-1]
        years = [year]

    # Compress adjacent years into periods
    periods = []
    period = []
    for year in years:
        if period and year-1 not in period:
            periods.append(period)
            period = []
        period.append(year)
    periods.append(period)

    signature = []
    for period in periods:
        if len(period) > 1:
            signature.append('%s-%s' % (min(period), max(period)))
        else:
            signature.append(str(period[0]))

    if owner is None:
        owner = m.group('owner')

    lead = m.group('lead')
    signature = ','.join(str(y) for y in signature)
    line = '%sCopyright (c) %s %s' % (lead, signature, owner)
    return line, True


def visit((owner, year, append), dirname, names):
    for name in list(names):
        if name.startswith('.'):
            # Avoid directories like .svn
            names.remove(name)
            continue
        if name.endswith('.egg-info'):
            names.remove(name)
            continue
        if os.path.splitext(name)[1] not in ['.c', '.h', '.txt', '.py']:
            continue
        if os.path.isfile(os.path.join(dirname, name)):
            path = os.path.join(dirname, name)
            file = open(path, 'r')
            fixed = fix_file(file, owner, year, append)
            open(path, 'w').write(fixed.getvalue())


def main():
    description = ('Update the copyright header of all Python files in a '
                   'given directory to include the current year.')
    parser = optparse.OptionParser(description=description)
    parser.add_option(
        '-d', '--directory', default='.',
        help='Directory to search for files to update. Default: %default')
    parser.add_option('-a', '--append', default=False, action='store_true',
        help='Only normalize existing copyright lines, append new lines'
             'for new data.')
    parser.add_option('-y', '--year', default=None, type='int',
                      help='Additional year to include in the copyright line')
    parser.add_option('-o', '--owner', default=None,
                      help='Owner identifier to replace with.')

    options, args = parser.parse_args()

    os.path.walk(options.directory, visit,
                 (options.owner, options.year, options.append))
