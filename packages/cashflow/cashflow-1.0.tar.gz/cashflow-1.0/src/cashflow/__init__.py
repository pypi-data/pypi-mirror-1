"""Cash flow analysis for GnuCash accounts."""

import gzip
import xml.etree.cElementTree as ET
from cashflow.book import Book

def open(path):
    """Open a GnuCash file and return a Book object that manages it."""
    tree = ET.parse(gzip.open(path))
    return Book(tree)

def sample_file_path():
    """Return the path to the Gnucash file included as a sample."""
    import os.path
    return os.path.join(os.path.dirname(__file__), 'sample.gnucash')
