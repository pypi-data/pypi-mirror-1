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

TEMPLATE_PATTERN = re.compile(
    '^(?P<lead>.*)Copyright \\(c\\) '
    '(?P<periods>[0-9\-, ]+) (?P<owner>.*)$')


def fix_file(file, owner, year):
    output = StringIO.StringIO()
    line_set = []
    for number, line in enumerate(file):
        if has_copyright(line):
            # First append copyright lines to the set
            line_set.append(line)
        elif line_set:
            # Then, if we have found lines and the block is done,
            # perform the update.
            for fixed in fix_block(line_set, year, owner):
                output.write(fixed)
            line_set = []
            output.write(line)
        else:
            # Just a regular line.
            output.write(line)
    return output


def has_copyright(line):
    return TEMPLATE_PATTERN.match(line) is not None


def fix_block(lines, new_year, new_owner):
    global_lead = None
    # Ensure consistent leads in all copyright statements
    for line in lines:
        m = TEMPLATE_PATTERN.match(line)
        assert m is not None
        lead = m.group('lead')
        if lead.strip() == '#':
            # Python copyright line
            pass
        elif lead.strip() == '':
            # C copyright line, embedded in multi-line comment
            pass
        else:
            raise ValueError('Invalid lead for copyright line', line)
        if global_lead is not None and lead != global_lead:
            raise ValueError('Inconsistent multi-line leads: %r vs %r'
                             (global_lead, lead))
        elif global_lead is None:
            global_lead = lead

    updated = False
    for line in lines:
        m = TEMPLATE_PATTERN.match(line)
        owner = m.group('owner')
        if owner == new_owner:
            # Found an existing entry, update.
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
                    raise ValueError('Invalid time period %r' % period)
                # A multi-year period
                first, last = period.split('-')
                years.update(range(int(first), int(last) + 1))

            years.add(new_year)
            years = sorted(years)

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

            signature = ','.join(str(y) for y in signature)
            line = '%sCopyright (c) %s %s\n' % (global_lead, signature, owner)
            updated = True
        yield line
    if not updated:
        yield '%sCopyright (c) %s %s\n' % (global_lead, new_year, new_owner)


def visit((owner, year), dirname, names):
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
            fixed = fix_file(file, owner, year)
            open(path, 'w').write(fixed.getvalue())


def main():
    description = ('Update the copyright header of all (Python) files in a '
                   'given directory to include a given year and copyright '
                   'holder.')
    parser = optparse.OptionParser(description=description)
    parser.add_option(
        '-d', '--directory', default='.',
        help='Directory to search for files to update. Default: %default')
    parser.add_option('-y', '--year', default=None, type='int',
                      help='Year to include in the copyright line')
    parser.add_option('-o', '--owner', default=None,
                      help='Owner identifier to set.')

    options, args = parser.parse_args()

    os.path.walk(options.directory, visit,
                 (options.owner, options.year))
