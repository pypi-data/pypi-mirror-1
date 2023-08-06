#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File Catalog Input/Output
=========================

Reading and writing of YAML files into/from a tree structure.

:copyright: 2006-2008 Jochen Kupperschmidt
:license: GNU General Public License, version 2; see LICENSE for details
"""

from __future__ import with_statement

import yaml


class DocumentProcessingError(Exception):
    """Indicating that reading, parsing or traversing the document failed."""


def load_file(filename):
    """Load tree structure from a file."""
    with open(filename, 'rb') as f:
        try:
            data = yaml.safe_load(f)
            if not data:
                raise DocumentProcessingError('No data found.')
        except Exception, exc:
            raise DocumentProcessingError('Error reading file.')
    if not isinstance(data, dict):
        raise DocumentProcessingError(
            'Invalid data. Expected hash/mapping/dictionary structure.')
    return data

def dump(data):
    """Dump data into a format suitable for file storage."""
    return yaml.safe_dump(data, default_flow_style=False)
