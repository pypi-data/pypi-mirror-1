# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Lists of integers and integer ranges.
"""


class RangeList(object):
    """A list of integers that may include ranges.
    """

    items = None

    def __init__(self, *args):
        self.items = []
        for item in args:
            if isinstance(item, RangeList):
                self.items.extend(item.items)
            else:
                self.items.append(item)

    def __len__(self):
        return sum(1 if isinstance(item, int) else item[1] - item[0]
                   for item in self.items)

    def __min__(self):
        item = self.items[0]
        return item if isinstance(item, int) else item[0]

    def __max__(self):
        item = self.items[-1]
        return item if isinstance(item, int) else item[1]

    def __iter__(self):
        for item in self.items:
            if isinstance(item, int):
                yield item
            else:
                for i in xrange(item[0], item[1]):
                    yield i

    def __contains__(self, value):
        for item in self.items:
            if isinstance(item, int):
                if item == value:
                    return True
            elif item[0] <= value < item[1]:
                return True
        else:
            return False

    def __repr__(self):
        return "RangeList(%s)" % repr(list(self.items))[1:-1]

    def __str__(self):
        return "[%s]" % ", ".join(str(item) if isinstance(item, int)
                                  else "%s -- %s" % (item[0], item[1]-1)
                                  for item in self.items)


def range_list(specs, upper):
    ranges = []
    for spec in specs:
        a, sep, b = spec.partition('-')
        if not sep:
            ranges.append(int(a))
        else:
            a = int(a) if a else 1
            b = int(b) if b else upper
            ranges.append((a, b+1))
    return RangeList(*ranges)
