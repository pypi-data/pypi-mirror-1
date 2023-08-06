""" Utilities for WhooshDoc.
"""

import os
import struct
import sys

from whoosh import index
from whoosh.fields import KEYWORD, Schema, TEXT


query_help = """
The Whoosh query syntax supports conjunctions with AND and OR, negation with
NOT, grouping with (parentheses), and phrases with "quotes". Once can use
the * wildcard at the end of a term, but not the beginning or middle. By
default, all search terms are ANDed together.

By default, search terms are applied to the docstring content itself. There
are additional fields that can be searched with the syntax
"field_name:search_expr". The fields are:

    - docstring: Just in case you want to be explicit.

    - name: The preferred name of the object. It may be any single part of
        the dotted name, or any number of leading parts of the name.
        For example, the function numpy.linalg.lstsq can be found in all the
        searches "name:lstsq", "name:numpy", "name:numpy.linalg", and
        "name:linalg".

    - aliases: All of the discovered names of the object, including the
        preferred one. When an object is created in one place, and exposed
        higher up in the package hierarchy, the higher name is "preferred".
        For example, if we have a function defined as foo.bar.baz() but is
        imported into the foo.__init__ module to be exposed as foo.baz(), it
        will have a "name" of foo.baz, but "aliases" will also have
        foo.bar.baz.

    - kind: Either "function", "class", "method" or "module" depending on
        the kind of object. For example, to find only functions (or
        methods), use "kind:function". To exclude modules, use "not
        kind:module".

    - summary: The docstring summary is the first contiguous paragraph in
        a docstring, usually just a sentence. While you can use this field
        to just search the summary sentence, this is not usually an
        improvement over just searching the docstring itself. This field is
        used to internally to show more informative results.

Examples
--------
bessel kind:function
    Find Bessel functions, but not modules that use the word "bessel".

bessel or airy not filter
    Find both Bessel functions and Airy functions but not Bessel filters.

name:linalg
    Look for anything with the component 'linalg' in its preferred name.

"minimize a function"
    Find docstrings with the phrase "minimize a function".

the
    Should return no results. Common English connective words like "the"
    (i.e. so-called "stop" words) are omitted during indexing and cannot be
    searched for.

name:fmin*
    Search for all objects with names that start with "fmin" like fmin_tnc,
    fmin, and fminbound.
"""

schema = Schema(
    # The kind of object.
    # 'module', 'class', 'function', or 'method'
    kind = KEYWORD(stored=True),
    # The preferred name of the object.
    name = KEYWORD(stored=True),
    # The group the docstring belongs to.
    group = KEYWORD(stored=True),
    # A space-separated list of aliases. The stored portion should not contain
    # the preferred name, but the indexed part should to simplify queries.
    aliases = KEYWORD(stored=True),
    # The whole docstring.
    docstring = TEXT(stored=True),
    # The first line of the docstring.
    summary = TEXT(stored=True),
)

def create_or_open_index(dirname):
    """ Open an index, or create it if necessary.
    """
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    if os.listdir(dirname):
        ix = index.open_dir(dirname)
    else:
        ix = index.create_in(dirname, schema=schema)
    return ix

def terminal_size():
    """ Return the width and height of the terminal in a cross-platform manner.
    """
    if sys.platform == 'win32':
        width, height = _terminal_size_win32()
    else:
        width, height = _terminal_size_unix()
    return width, height

def _terminal_size_win32():
    """ Return the width and height of the terminal on 32-bit Windows.

    This code derives from the Python Cookbook recipe by Alexander Belchenko
    available under the PSF license.
    http://code.activestate.com/recipes/440694/
    """
    from ctypes import windll, create_string_buffer

    width = 80
    height = 25

    # FIXME: wrap with a try: except:? What exceptions might I get?
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

    if res:
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        width = right - left + 1
        height = bottom - top + 1
    # Windows consoles appear to treat the \n as a character.
    width -= 1
    return width, height

def _terminal_size_unix():
    """ Return the width and height of the terminal on UNIX-type systems.
    """
    width = -1
    height = -1
    try:
        import fcntl
        import termios
        height, width = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(),
            termios.TIOCGWINSZ, '1234'))
    except (ImportError, AttributeError, IOError), e:
        pass
    if width <= 0:
        width = os.environ.get('COLUMNS', -1)
    if height <= 0:
        height = os.environ.get('LINES', -1)
    if width <= 0:
        width = 80
    if height <= 0:
        height = 25
    return width, height

def default_index():
    """ Try to find the default index.

    First, the egg entry point "WhooshDoc.index" is checked, then "_index" is
    assumed.
    """
    try:
        import pkg_resources
        ep = iter(pkg_resources.iter_entry_points('WhooshDoc.index')).next()
        indexname = ep.load(require=False)
    except (ImportError, StopIteration), e:
        indexname = '_index'
    return indexname
        
