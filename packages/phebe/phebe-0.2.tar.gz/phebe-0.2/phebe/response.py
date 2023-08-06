# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Parsing the response to AT commands.
"""

import phebe.rangelist


def parseResponse(line):
    """Parse a response line into a list of values of appropriate data types.

    line: unicode, response line stripped of AT command prefix and whitespace

    returns list of objects
    """
    results = [[]]
    while line:
        # open nested lists
        while line.startswith('('):
            results.append([])
            line = line[1:]

        # collect a value
        if line.startswith(')'):
            last = results.pop()
            results[-1].append(last)
            line = line[1:]
        elif line.startswith(','):
            results[-1].append(None)
        elif line.startswith('"'):
            value, sep, line = line[1:].partition('"')
            results[-1].append(value)
        else:
            value = line.partition(')')[0].partition(',')[0]
            line = line[len(value):]
            try:
                if '-' in value:
                    first, sep, last = value.partition('-')
                    results[-1].append(phebe.rangelist.RangeList(
                        (int(first), int(last)+1)))
                else:
                    results[-1].append(int(value))
            except ValueError:
                results[-1].append(value.encode("utf-8"))

        if line.startswith(','):
            line = line[1:]

    assert len(results) == 1
    return results[0]
