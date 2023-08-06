""" Main entry point for the wdoc script.
"""

import logging
import sys
import time

from argparse import RawDescriptionHelpFormatter
from whoosh import index
from whoosh.query import Or, Term

from whooshdoc.argcmd import ArgCmd, argument, kwds
from whooshdoc.search import ResultsMenu
from whooshdoc.util import create_or_open_index, default_index, query_help


logger = logging.getLogger(__name__)


def soft(text):
    """ Write the text to STDOUT with a newline, but with flushing.
    """
    sys.stdout.write(text)
    sys.stdout.flush()


class Commands(ArgCmd):
    """ Manipulate and query WhooshDoc indices.
    """
    main_args = [
        argument('-i', '--index',
            help="The directory containing the Whoosh index."),
        argument('-v', '--verbose', action='store_true'),
    ]

    def postprocess_args(self, args):
        """ Postprocess the parsed arguments.
        """
        if not args.verbose:
            logging.disable(logging.CRITICAL+1)
        else:
            logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        # TODO: check default locations?
        if args.index is None:
            args.index = default_index()
        return args

    @argument('-g', '--group',
        help="The name of the group to apply. [default: the first package]")
    @argument('packages', nargs="+", metavar="PACKAGE",
        help="The name(s) of packages to start the search for docstrings.")
    def index(self, args):
        """ Collect docstrings from some packages and index them.
        """
        # Local import to prevent dependencies on epydoc for querying.
        from whooshdoc.indexem import get_docstrings, index_docstrings
        soft('Searching for docstrings ... ')
        t0 = time.time()
        values, variables = get_docstrings(args.packages)
        print 'done.'
        t1 = time.time()
        print '  Took %.2f s' % (t1 - t0)

        ix = create_or_open_index(args.index)
        soft('Indexing %s docstrings ... ' % len(values))
        t0 = time.time()
        index_docstrings(ix, values, variables, args.group)
        print 'done.'
        t1 = time.time()
        print '  Took %.2f s' % (t1 - t0)

    @argument('groups', nargs='+', metavar='GROUP', type=unicode,
        help="The name(s) of the groups to delete.")
    def delgroups(self, args):
        """ Delete groups of docstrings from the index.
        """
        query = Or([Term('group', g) for g in args.groups])
        ix = index.open_dir(args.index)
        ndeleted = ix.delete_by_query(query)
        print '%s docstrings deleted.' % ndeleted

    @argument('terms', nargs='+', metavar='TERM',
        help="The Whoosh query terms.")
    @kwds(epilog=query_help, formatter_class=RawDescriptionHelpFormatter)
    def search(self, args):
        """Search the index and print out the names of the objects found."""
        query_string = u' '.join(args.terms)
        ix = index.open_dir(args.index)
        ResultsMenu.query(ix, query_string).mainloop()

    @argument('terms', nargs='*', metavar='TERM',
        help="Optional Whoosh query terms to start with.")
    @kwds(epilog=query_help, formatter_class=RawDescriptionHelpFormatter)
    def ui(self, args):
        """Bring up a wxPython UI."""
        from whooshdoc.ui.search import SearchUI, ThreadedSearcher
        ds = ThreadedSearcher.fromdirname(args.index)
        # FIXME: Just setting the query string here does not appear to trigger
        # a search, so we must do it explicitly.
        ds.query_string = u' '.join(args.terms)
        ds.search()
        ui = SearchUI(model=ds)
        ui.configure_traits()

def main():
    Commands().run()

if __name__ == '__main__':
    main()

