import re
from string import whitespace

from whoosh.qparser import QueryParser

from whooshdoc.util import terminal_size


class ResultsMenu(object):
    """ Present query results in a terminal interactively.
    """

    def __init__(self, results):
        self.results = results

        # The first result currently displayed.
        self.top_result = 0
        # The next result after the last displayed result. It may not be a real
        # result.
        self.next_result = min(len(self.results), self.get_displayable_num_results())

    def reset_terminal_size(self):
        """ Reset the terminal size based on the current settings.
        """
        self.width, self.height = terminal_size()

    def get_displayable_num_results(self):
        """ Get the number of displayable results.
        """
        self.reset_terminal_size()
        # Omit 4 lines:
        # 1 for header
        # 2 for empty lines
        # 1 for prompt.
        avail_lines = self.height - 4
        # Decide how many results we can display.
        # 1 line for the name
        # 1 line for the summary
        # 1 empty line for readability.
        nresults = avail_lines // 3
        return nresults

    def next_page(self):
        """ Move forward by a page.
        """
        if self.next_result >= len(self.results):
            # Already at the last page.
            return
        nresults = self.get_displayable_num_results()
        self.top_result = self.next_result
        self.next_result = min(len(self.results), self.next_result + nresults)

    def prev_page(self):
        """ Move backward by a page.
        """
        nresults = self.get_displayable_num_results()
        self.top_result = max(0, self.top_result - nresults)
        self.next_result = min(len(self.results), self.top_result + nresults)

    def show_page_with_summaries(self):
        """ Show the current page of results.
        """
        if len(self.results) == 0:
            top = 0
        else:
            top = self.top_result + 1
        header = 'Showing results %s-%s of %s:' % (top, self.next_result,
            len(self.results))
        print header
        print
        for i in range(self.top_result, self.next_result):
            self.show_result_with_summary(i)
        print

    def elide_summary(self, summary):
        """ Elide and format a summary sentence for display.
        """
        words = summary.strip(whitespace + '-=~').split()
        summary = ' '.join(words)
        nindent = 6
        indent = ' '*nindent
        avail_columns = self.width - nindent
        if len(summary) > avail_columns:
            summary = summary[:avail_columns-4] + ' ...'
        return indent + summary

    def show_result_with_summary(self, i):
        """ Show a single result with a (possibly elided) summary line.
        """
        result = self.results[i]
        kind = result.get('kind', 'unknown')
        print '%4s: %-50s [%s]' % (i+1, result.get('name', '<no name>'), kind)
        summary = self.elide_summary(result.get('summary', 'No summary.'))
        print summary
        print

    def is_int(self, string):
        """ Return True if a string is a positive integer.
        """
        return re.match(r'\d+', string) is not None

    def is_name(self, string):
        """ Return True if a string is a dotted name.
        """
        regex = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*')
        return regex.match(string) is not None

    def help(self, name):
        """ View the docstring (or other help text) of the particular object.

        This can be overridden in subclasses in order to integrate with other
        help mechanisms. The default is to use the builting help().

        Parameters
        ----------
        name : unicode or str
            The full dotted name of the indexed object.
        """
        # help() does not interpret unicode strings as names.
        name = str(name)
        help(name)

    def mainloop(self):
        """ Main loop.
        """
        self.show_page_with_summaries()
        if len(self.results) == 0:
            # Don't bother prompting. There's nothing a user can do.
            return
        while True:
            try:
                response = raw_input('Type number or name to view item '
                    '(q to quit, n/p to navigate): ').strip()
            except (EOFError, KeyboardInterrupt), e:
                # User Ctrl-D'ed.
                break
            if response.lower() == 'q':
                break
            elif response.lower() == 'n':
                self.next_page()
                self.show_page_with_summaries()
            elif response.lower() == 'p':
                self.prev_page()
                self.show_page_with_summaries()
            elif response == '':
                # Just pressing Enter will advance.
                self.next_page()
                self.show_page_with_summaries()
            elif self.is_int(response):
                i = int(response) - 1
                if 0 <= i <= len(self.results):
                    name = self.results[i]['name']
                    self.help(name)
                self.show_page_with_summaries()
            elif self.is_name(response):
                help(response)
                self.show_page_with_summaries()
            else:
                print 'Could not understand input.'

    @classmethod
    def query(cls, ix, query_string, funcs_first=False):
        """ Create from an index and a query.

        Parameters
        ----------
        ix : Index
            A Whoosh Index.
        query_string : unicode
            A Whoosh-format query.
        funcs_first : bool, optional
            Sort the results to make functions appear before classes then
            modules in the result list.
        """
        searcher = ix.searcher()
        p = QueryParser('docstring', schema=ix.schema)
        query = p.parse(query_string)
        if query is None or query.normalize() is None:
            results = []
        else:
            results = list(searcher.search(query))
        if funcs_first:
            kinds = {
                'function': 0,
                'class': 1,
                'module': 2,
                'method': 3,
            }
            results.sort(key=lambda d: kinds.get(d.get('kind', None), 100))
        return cls(results)


