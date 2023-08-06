#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" A GUI search widget.
"""

import logging
from string import whitespace
import textwrap
import threading

from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.support.pyparsing import ParseException

from enthought.traits.api import (Any, Bool, Event, Float, Font, HTML, 
    HasTraits, List, Property, Unicode, on_trait_change)
from enthought.traits.ui import api as tui
from enthought.traits.ui.tabular_adapter import TabularAdapter


logger = logging.getLogger(__name__)


def html_escape(s):
    """ Escape a string for inclusion in HTML.
    """
    s = (s.replace('&', '&amp;')
          .replace('<', '&lt;')
          .replace('>', '&gt;')
          .replace('"', '&quot;')
          .replace("'", '&#39;'))
    return s


class DocstringSearcher(HasTraits):
    """ Search a WhooshDoc index.
    """

    #### Configuration traits ##################################################

    # The Index.
    index = Any()

    # Whether to resort functions and methods to come first.
    funcs_first = Bool(True)


    #### State traits ##########################################################

    # The query string.
    query_string = Unicode()

    # The current results.
    results = List()

    # Trigger the search.
    do_search = Event()


    @classmethod
    def fromdirname(cls, dirname, **traits):
        """ Create from the directory name of the index.
        """
        traits['index'] = index.open_dir(dirname)
        return cls(**traits)

    @on_trait_change('do_search')
    def _do_search(self):
        self.search()

    def search(self):
        """ Parse the query string and perform the search.
        """
        searcher = self.index.searcher()
        p = QueryParser('docstring', schema=self.index.schema)
        try:
            query = p.parse(self.query_string)
        except ParseException:
            # Bad query.
            self.results = []
            return
        except Exception, e:
            # Bad query. Might be a bug in the parser, though, so log it.
            logger.exception('Could not parse query %r', self.query_string)
            self.results = []
            return
        if query is None or query.normalize() is None:
            results = []
        else:
            results = list(searcher.search(query))
        if self.funcs_first:
            kinds = {
                'function': 0,
                'class': 1,
                'module': 2,
                'method': 3,
            }
            results.sort(key=lambda d: kinds.get(d.get('kind', None), 100))
        self.results = results


class ThreadedSearcher(DocstringSearcher):
    """ Search model that responds to queries by searching in a separate thread.
    """

    # The worker thread.
    worker = Any()

    # Notify the worker thread that there is a new query to search.
    new_query = Any()


    def __init__(self, **traits):
        super(ThreadedSearcher, self).__init__(**traits)

        # Create the threaded stuff on initialization.
        self.new_query = threading.Event()

        t = threading.Thread(target=self._thread_main)
        t.daemon = True
        t.start()

        self.worker = t

    @on_trait_change('do_search')
    def _do_search(self):
        self.new_query.set()

    def _thread_main(self):
        """ Wait to be notified that we have a new query.
        """
        while True:
            self.new_query.wait()
            self.new_query.clear()
            self.search()


class ResultAdapter(TabularAdapter):
    """ Adapt a result dict for the TabularEditor.
    """

    normal_font = Font("Arial 9")

    columns = [
        ('Name', 'the_name'),
        ('Kind', 'kind'),
        ('Summary', 'summary'),
    ]

    the_name_text = Property(depends_on=['item'])
    kind_text = Property(depends_on=['item'])
    summary_text = Property(depends_on=['item'])

    the_name_width = Float(150.0)
    kind_width = Float(60.0)  # 50 is okay for OS X, but 60 for Windows.


    def get_font(self, object, trait, row):
        """ The default font is to tall for the table rows.  sigh...             
        """
        return self.normal_font
    
    def _get_the_name_text(self):
        if self.item is None:
            return u''
        return self.item['name']

    def _get_kind_text(self):
        if self.item is None:
            return u''
        return self.item['kind']

    def _get_summary_text(self):
        if self.item is None:
            return u''
        raw = self.item.get('summary', u'')
        words = raw.strip(whitespace + '-=~').split()
        summary = u' '.join(words)
        return summary


class SearchUI(tui.Controller):
    """ UI for searching a WhooshDoc index.
    """

    # The selected item.
    selected = Any()

    # The selected docstring.
    docstring = Property(HTML, depends_on=['selected'])


    query_group = tui.VGroup(
# FIXME: Extract the nice SearchEditor from BlockCanvas to use for the query.
#            editor=SearchEditor(
#                search_event_trait="do_search",
#                text='Search for docstrings',
#                enter_set=True,
#            ),
        tui.Group(
            tui.Item('query_string',
                editor=tui.TextEditor(
                    enter_set=True,
                    auto_set=True,
                ),
                label='Search:'
            ),
        ),
        tui.UItem('results',
            editor=tui.TabularEditor(
                adapter=ResultAdapter(),
                editable=False,
                selected="controller.selected",
            ),
        ),
    )

    traits_view = tui.View(
        tui.HGroup(
            query_group,
            tui.VGroup(
                tui.UItem('controller.docstring',
                    style='readonly',
                ),
            ),
        ),
        width=1024,
        height=768,
        resizable=True,
        title='WhooshDoc!',
    )

    @on_trait_change('model.query_string')
    def _send_event(self):
        self.model.do_search = True

    def _get_docstring(self):
        """ Format the docstring for viewing.
        """
        if self.selected is None:
            return u''
        docstring = self.selected.get('docstring', u'No docstring.')
        lines = docstring.splitlines()
        firstline = lines[0]
        body = u'\n'.join(lines[1:])
        body = textwrap.dedent(body)
        # FIXME: the next line of body might still be indented. We should
        # probably try to match it.
        text = u'%s\n%s' % (firstline, body)
        # The wx HTML widget does not properly respect <pre> tags, so we have to
        # do it manually.
        text = html_escape(text.expandtabs())
        lines = text.replace(' ', '&nbsp;').splitlines()
        elems = ['<code>%s</code><br />' % line for line in lines]
        html = '\n'.join(elems)
        return html
