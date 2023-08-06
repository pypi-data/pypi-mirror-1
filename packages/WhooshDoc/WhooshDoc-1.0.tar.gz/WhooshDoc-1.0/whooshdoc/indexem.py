#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement

from collections import defaultdict
from contextlib import contextmanager
import logging

from epydoc import apidoc, docbuilder, docstringparser, docintrospecter, log


logger = logging.getLogger(__name__)


indexed_docs = (apidoc.ClassDoc, apidoc.ClassMethodDoc, apidoc.ModuleDoc,
    apidoc.PropertyDoc, apidoc.RoutineDoc, apidoc.StaticMethodDoc)
api_modules = ('api', '__init__')


@contextmanager
def safe_epydoc():
    old_fields = docstringparser.STANDARD_FIELDS[:]
    old_docformat = docstringparser.DEFAULT_DOCFORMAT
    del docstringparser.STANDARD_FIELDS[:]
    docstringparser.DEFAULT_DOCFORMAT = 'plaintext'
    yield None
    docstringparser.STANDARD_FIELDS[:] = old_fields
    docstringparser.DEFAULT_DOCFORMAT = old_docformat


class EpydocLoggerAdapter(log.Logger):
    """ Adapt a logging.Logger to a epydoc.log.Logger.
    """
    def __init__(self):
        self.logger = logging.getLogger('epydoc')

    def log(self, level, message):
        self.logger.log(level, message)

log.register_logger(EpydocLoggerAdapter())

def in_packages(name, package_names):
    """ Return True if a DottedName is a (nonstrict) child of one of a sequence
    of DottedNames.
    """
    for pkg in package_names:
        if pkg.dominates(name, strict=False):
            return True
    return False

def traverse(docindex, packages, **filters):
    """ Return a list of desired ValueDocs that can be reached by the index and
    their various locations.
    """
    apidoc_queue = list(docindex.root)
    val_set = set()
    var_set = set()
    accepted_values = set()
    variables = defaultdict(set)
    while apidoc_queue:
        api_doc = apidoc_queue.pop()
        if isinstance(api_doc, apidoc.ValueDoc):
            val_set.add(api_doc)
            the_value = api_doc
            the_variable = None
        else:
            var_set.add(api_doc)
            the_value = api_doc.value
            the_variable = api_doc
        if (isinstance(the_value, indexed_docs) and
            in_packages(the_value.canonical_name, packages)):
            if the_variable is not None and the_variable.canonical_name != the_value.canonical_name:
                variables[the_value].add(the_variable)
            accepted_values.add(the_value)
        apidoc_queue.extend([v for v in api_doc.apidoc_links(**filters)
                             if v not in val_set and v not in var_set])
    return accepted_values, variables

def get_preferred_names(value, variables):
    """ Get the preferred name and preferred aliases for an object.
    """
    canonical_name = value.canonical_name
    if isinstance(value, apidoc.ModuleDoc):
        return canonical_name, []
    elif len(variables) == 0:
        return canonical_name, []
    else:
        # General case. We've already filtered out the variables that are just
        # the defining location of the value.
        good_aliases = [canonical_name]
        for var in variables:
            module = var.defining_module
            mod_name = module.canonical_name
            if module.is_package is apidoc.UNKNOWN:
                # Some APIDocs aren't initialized enough. They shouldn't be
                # relevant.
                continue
            elif ((module.is_package and mod_name.dominates(canonical_name) or
                (mod_name[-1] == 'api' and mod_name.container().dominates(canonical_name)))):
                # Assume this was an intentional exposing.
                good_aliases.append(var.canonical_name)
        # Now pick out the preferred name.
        lengths = defaultdict(list)
        for name in good_aliases:
            lengths[len(name)].append(name)
        min_length = min(lengths)
        all_the_best = lengths[min_length]
        if len(all_the_best) == 1:
            best = lengths[min_length][0]
        else:
            # We might have intentional aliases like numpy.bool_, numpy.bool8,
            # etc. Prefer the one with the same final name as the canonical
            # name.
            for name in all_the_best:
                if name[-1] == canonical_name[-1]:
                    best = name
                    break
            else:
                # Nope. Pick an arbitrary one.
                best = all_the_best[0]
        good_aliases.remove(best)
        return best, good_aliases

def name_keywords(names):
    """ Create keywords for a list of names to include all leading parts of the
    names.
    """
    parts = set()
    for name in names:
        for i in range(len(name)):
            parts.add(str(name[:i+1]))
            parts.add(name[i])

    return u' '.join(sorted(parts))

def as_document(value, variables):
    """ Create a document dict for indexing.
    """
    best, aliases = get_preferred_names(value, variables)
    if isinstance(value, apidoc.ModuleDoc):
        kind = u'module'
    elif isinstance(value, apidoc.ClassDoc):
        kind = u'class'
    else:
        # Quick heuristic to determine if something is a method or a function.
        if value.defining_module is apidoc.UNKNOWN:
            raise ValueError("Value for %s does not have a defining module. "
                "Skipping." % value.canonical_name)
        elif value.canonical_name.container() == value.defining_module.canonical_name:
            kind = u'function'
        else:
            kind = u'method'
    if value.summary is not None and value.summary is not apidoc.UNKNOWN:
        summary = value.summary.to_plaintext(None)
        if isinstance(summary, str):
            summary = unicode(summary)
        elif not isinstance(summary, unicode):
            raise TypeError("summary for %s is a %r : %r" % (best, type(summary), summary))
    else:
        summary = u''
    if value.docstring is not None and value.docstring is not apidoc.UNKNOWN:
        docstring = value.docstring
        if isinstance(docstring, str):
            docstring = unicode(docstring)
        elif not isinstance(docstring, unicode):
            raise TypeError("docstring for %s is a %r : %r" % (best, type(docstring), docstring))
    else:
        docstring = u''

    doc = dict(
        kind = kind,
        name = name_keywords([best]),
        _stored_name = unicode(best),
        aliases = name_keywords([best] + aliases),
        _stored_aliases = u' '.join(map(unicode, aliases)),
        docstring = docstring,
        summary = summary,
    )
    return doc

def get_docstrings(roots, clear_cache=False, exclude_regexes=None):
    """ Get docstrings for items under the given root packages.
    """
    with safe_epydoc():
        if clear_cache:
            docintrospecter.clear_cache()
        kwds = {}
        if exclude_regexes is not None:
            regex = '|'.join(exclude_regexes)
            kwds['exclude_introspect'] = regex
            kwds['exclude_parse'] = regex
        docindex = docbuilder.build_doc_index(roots, **kwds)
        if docindex is None:
            raise RuntimeError("epydoc logged an exception. Could not document "
                "something in %r" % (roots,))
        packages = [apidoc.DottedName(r) for r in roots]
        values, variables = traverse(docindex, packages)
    return values, variables

def index_docstrings(ix, values, variables, group=''):
    """ Add docstrings to the index.
    """
    writer = ix.writer()
    with writer:
        for value in sorted(values, key=lambda d: d.canonical_name):
            doc = as_document(value, variables[value])
            writer.add_document(group=group, **doc)

