"""CNV utilities."""
from __future__ import absolute_import, division, print_function
import sys
import os.path

import numpy
from Bio.File import as_handle

from .ngfrills import echo, safe_write

# __________________________________________________________________________
# I/O helpers

def parse_tsv(infile, keep_header=False):
    """Parse a tabular data table into an iterable of lists.

    Rows are split on tabs.  Header row is optionally included in the output.
    """
    with as_handle(infile) as handle:
        lines = iter(handle)
        header = next(lines)
        if keep_header:
            yield header.rstrip().split('\t')
        for line in lines:
            yield line.rstrip().split('\t')


def write_tsv(outfname, table, colnames=None):
    """Write the CGH file."""
    if not outfname:
        outfname = sys.stdout
    with safe_write(outfname) as handle:
        if colnames:
            header = '\t'.join(colnames) + '\n'
            handle.write(header)
        handle.writelines('\t'.join(map(str, row)) + '\n'
                           for row in table)


# __________________________________________________________________________
# Sorting key functions


def sorter_chrom(label):
    """Create a sorting key from chromosome label.

    Sort by integers first, then letters or strings. The prefix "chr"
    (case-insensitive), if present, is stripped automatically for sorting.

    E.g. chr1 < chr2 < chr10 < chrX < chrY
    """
    chrom = (label[3:] if label.lower().startswith('chr')
             else label)
    return (chr(int(chrom)) if chrom.isdigit()
            else chrom)


def sorter_chrom_at(index):
    """Create a sort key function that gets chromosome label at a list index."""
    return lambda row: sorter_chrom(row[index])


# __________________________________________________________________________
# More helpers

def assert_equal(msg, **values):
    """Evaluate and compare two or more values for equality.

    Sugar for a common assertion pattern. Saves re-evaluating (and retyping)
    the same values for comparison and error reporting.

    Example:

    >>> assert_equal("Mismatch", expected=1, saw=len(['xx', 'yy']))
    ...
    ValueError: Mismatch: expected = 1, saw = 2

    """
    ok = True
    key1, val1 = values.popitem()
    msg += ": %s = %r" % (key1, val1)
    for okey, oval in values.iteritems():
        msg += ", %s = %r" % (okey, oval)
        if oval != val1:
            ok = False
    if not ok:
        raise ValueError(msg)


def check_unique(items, title):
    """Ensure all items in an iterable are identical; return that one item."""
    its = set(items)
    assert len(its) == 1, ("Inconsistent %s keys: %s"
                           % (title, ' '.join(map(str, sorted(its)))))
    return its.pop()


def fbase(fname):
    """Strip directory and all extensions from a filename."""
    return os.path.basename(fname).split('.', 1)[0]


def rbase(fname):
    """Strip directory and final extension from a filename."""
    return os.path.basename(fname).rsplit('.', 1)[0]
