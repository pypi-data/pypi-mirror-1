#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File Catalog Indexer
====================

Traverse path and write a directory/filename tree structure to a file.

:copyright: 2006-2008 Jochen Kupperschmidt
:license: GNU General Public License, version 2; see LICENSE for details
"""

import os
import sys

from filecatalog import io


def walk(top):
    """Recursively traverse subdirectories.

    A hierarchical data structure with directory and file names is returned.
    """
    try:
        names = os.listdir(top)
    except os.error, err:
        return

    dirs = []
    non_dirs = []
    for name in names:
        path = os.path.join(top, name)
        if os.path.isdir(path) and not os.path.islink(path):
            dirs.append(walk(path))
        else:
            non_dirs.append(name)
    dirs.sort()
    non_dirs.sort()

    return {os.path.basename(top): dirs + non_dirs}

def main(path):
    """Index the given directory and write the YAML data to STDOUT."""
    sys.stdout.write(io.dump(walk(path)))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s <directory>' % os.path.basename(sys.argv[0])
        sys.exit(2)
    main(sys.argv[1])
