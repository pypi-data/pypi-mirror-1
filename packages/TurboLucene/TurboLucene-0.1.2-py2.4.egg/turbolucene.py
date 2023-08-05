#==============================================================================
#
# Copyright (c) 2007 Krys Wilken
#
# This software is licensed under the MIT license.  See the LICENSE file for
# licensing information.
#
#==============================================================================

"""turbolucene -- Provides search functionality for TurboGears using PyLucene.

Uses PyLucene to do all the heavy lifting, but as a result this module does
some fancy things with threads.

Note: Right now only English is supported for stemming, etc.

PyLucene requires that all threads that use it must inherit from
PythonThread.  This means either patching CherryPy and/or TurboGears, or
having the CherryPy thread hand off requests to PythonThreads and, in the
case of searching, wait for the result.  I have chosen the second method
so I don't have the maintain a patched CherryPy or TurboGears.

The other advantage to the chosen method is that indexing happens in a
separate thread so the web request can return more quickly by not waiting for
the results.

The main disadvantage with PyLucene and CherryPy, however, is that autoreload
does not work with it.  You *have* to disable it by adding
"autoreload.on = False" to your dev.cfg.

"""


#---Standard library imports

from Queue import Queue
from os.path import exists
from logging import getLogger
from atexit import register

#---Framework imports

from turbogears import scheduler

#--- Third-party imports

from PyLucene import (PythonThread, IndexModifier, SnowballAnalyzer, JavaError,
  StopAnalyzer, Document, Field, Term, IndexSearcher, MultiFieldQueryParser)


#---Globals

__revision__ = '$Id: turbolucene.py 23 2007-02-11 06:08:07Z krys $'
__all__ = ['start', 'add', 'update', 'remove', 'search', 'Document', 'Field',
  'STORE', 'COMPRESS', 'TOKENIZED', 'UN_TOKENIZED']
log = getLogger('turbolucene')
# These will hold singleton classes.
_indexer = _searcher_factory = None
# These will hold user-supplied objects
_make_document = _results_formatter = _search_fields = None
#TODO: These should be configurable.
_index_directory = 'index'
_analyzer = SnowballAnalyzer('English',  StopAnalyzer.ENGLISH_STOP_WORDS)

#---Convenience Globals

STORE = Field.Store.YES
COMPRESS = Field.Store.COMPRESS
TOKENIZED = Field.Index.TOKENIZED
UN_TOKENIZED = Field.Index.UN_TOKENIZED

#---Functions

def _stop():
    """Shutdown search engine threads."""
    _searcher_factory.close()
    _indexer.close()
    log.info(u'Search engine stopped.')

def _optimize():
    """Tell the search engine to optimize it's index."""
    _indexer('optimize')

def start(make_document, search_fields, results_formatter = None):
    """Initialise the search engine.

    This functions starts the search engine threads, makes sure the search
    engine will be shutdown upon shutdown of TurboGears and starts the
    optimisation scheduler to run every night at midnight.

    make_document is a function that will return a PyLucene Document object
    based on the object passed in to add(), update() or remove().  The Document
    object must have at least a field called 'id' that is a string.  This
    function operates inside a PyLucene PythonThread.

    search_fields is a list of Document object fields to search.  These fields
    are created by make_document and these are the fields to search by default.

    results_formatter, if provided, is a function that will return a formatted
    version of the search results that are passed to it by search().  Generally
    the results_formatter will take the list of ID strings that is passed to it
    and return a list of application-specific objects (like SQLObject
    instances, for example.)  This function operates outside of any PyLucene
    PythonThread (like in a CherryPy thread, for example) and so can safely
    access your model objects and request info.

    Example make_document function:
    ===============================

    def make_document(entry):
        '''Make a new PyLucene Document instance from an Entry instance.'''
        document = Document()
        document.add(Field('id', str(entry.id), STORE, UN_TOKENIZED))
        document.add(Field('posted_on', entry.rendered_posted_on, STORE,
          TOKENIZED))
        document.add(Field('title', entry.title, STORE, TOKENIZED))
        document.add(Field('text', strip_tags(entry.etree), COMPRESS,
          TOKENIZED))
        categories = ' '.join([unicode(category) for category in
          entry.categories])
        document.add(Field('category', categories, STORE, TOKENIZED))
        return document

    Example results_formatter function:
    ===================================

    def results_formatter(results):
        '''Return the results as SQLObject instances.

        Returns either an empty list or a SelectResults object.

        '''
        if results:
            return Entry.select_with_identity(IN(Entry.q.id, [int(id) for id in
              results]))

    """
    global _indexer, _searcher_factory, _make_document, _search_fields, \
      _results_formatter
    _indexer = Indexer(not exists('index') and True or False)
    _searcher_factory = SearcherFactory()
    _make_document = make_document
    _search_fields = search_fields
    _results_formatter = results_formatter
    # using atexit insted of call_on_shutdown so that tg-admin shell will also
    # shutdown properly.
    register(_stop)
    #TODO: The schedule should be configurable.
    scheduler.add_weekday_task(_optimize, range(1, 8), (00, 00))
    log.info(u'Search engine started.')

def add(entry):
    """Tell the search engine to add the given entry to the index.

    This function returns immediately.  It does not wait for the indexer to be
    finished.

    entry can be any object that make_document know how to handle.

    """
    _indexer('add', entry)

def update(entry):
    """Tell the the search engine to update the index for the given entry.

    This function returns immediately.  It does not wait for the indexer to be
    finished.

    entry can be any object that make_document know how to handle.

    """
    _indexer('update', entry)

def remove(entry):
    """Tell the search engine to remove the given entry from the index.

    This function returns immediately.  It does not wait for the indexer to be
    finished.

    entry can be any object that make_document know how to handle.

    """
    _indexer('remove', entry)

def search(query):
    """Get results from the search engine and return matching entries.

    If a results_formatter function was passed to start() then the results will
    be passed through the formatter before returning.  If not, results is a
    list of strings that are the IDs of matching entries.

    """
    results = _searcher_factory()(query)
    if _results_formatter:
        return _results_formatter(results)
    return results


#---Classes

class Indexer(PythonThread):

    """Responsible for updating and maintaining the search engine index.

    A single Indexer thread is created to handle all index modifications.

    Once the thread is started, messages are sent to it by calling the instance
    with a task and an entry, where task is one of the following strings:

     * add: Adds the entry to the index.
     * remove: Removes the entry from the index.
     * update: Updates the index of an entry.

    and entry is any object that make_document know how to handle.

    To properly shutdown the thread, call the close() method.

    """

    #---Public API

    def __init__(self, create=False):
        """Constructor.  Initialises message queue and PyLucene index.

        Instantiating this class starts the thread automatically.

        """
        PythonThread.__init__(self) # PythonThread is an old-style class
        self._queue = Queue()
        self._index = IndexModifier(_index_directory, _analyzer, create)
        self.start()

    def __call__(self, task, entry=None):
        """Put task and entry on the message queue for processing."""
        self._queue.put((task, entry))

    def close(self):
        """Send the close message to the thread and wait for it to stop."""
        self('close')
        self.join()

    #---Threaded methods

    def run(self):
        """Dispatch based on message in queue.

        Expects that queue will contain 2-tuples in the form of (task, entry),
        where task is one of 'add', 'update', 'remove', 'optimize' or 'close'
        and entry is any object that make_document can handle or None in the
        case of 'optimize' and 'close'.

        If the task is 'close', the thread shuts down.

        """
        while True:
            message, entry = self._queue.get()
            assert message in ('add', 'update', 'remove', 'optimize', 'close')
            getattr(self, '_' + message)(entry)
            if message == 'close':
                break
            self._index.flush() # This is essential.

    def _add(self, entry, document=None):
        """Add a new entry to the index."""
        if not document:
            document = _make_document(entry)
        log.info(u'Adding entry "%s" (id %s) to index.' % (unicode(entry),
          document['id']))
        self._index.addDocument(document)

    def _remove(self, entry, document=None):
        """Remove an entry from the index."""
        if not document:
            document = _make_document(entry)
        log.info(u'Removing entry "%s" (id %s) from index.' % (unicode(entry),
          document['id']))
        self._index.deleteDocuments(Term('id', document['id']))

    def _update(self, entry):
        """Update an entry in the index by replacing it."""
        document = _make_document(entry)
        self._remove(entry, document)
        self._add(entry, document)

    def _optimize(self, dummy):
        """Optimize the index.  This can take a while."""
        log.info(u'Optimising index.')
        self._index.optimize()
        log.info(u'Index optimized.')

    def _close(self, dummy):
        """Shutdown the index."""
        self._index.close()


class Searcher(PythonThread):

    """Responsible for searching the index and returning results.

    Searcher threads are created for each search that is requested.

    To search, instantiate a Search class and then call it with the query.  It
    returns the results as a list of entry ID strings and then the thread dies.
    The thread is garbage collected when it goes out of scope.

    The catch to all this is that a CherryPy thread cannot directly instantiate
    a Searcher thread because of PyLucene restrictions.  So to get around that,
    see the SercherFactory class.

    """

    def __init__(self):
        """Constructor.  Initialise message queues and starts the thread."""
        PythonThread.__init__(self) # PythonThread is an old-style class
        self._query_queue = Queue()
        self._results_queue = Queue()
        self.start()

    def __call__(self, query):
        """Send query to the thread, then wait for and return the results."""
        self._query_queue.put(query)
        results = self._results_queue.get()
        # The join was causing a segfault and I don't know why.  In theory the
        # join should not be necessary, but I thought it good practice to
        # include it.  Apparently that was a mistake.
##        self.join()
        return results

    def run(self):
        """Search the index for the sent query and send back the results.

        The results is a list of entry ID strings.  The thread dies after one
        search.

        """
        searcher = IndexSearcher(_index_directory)
        parser = MultiFieldQueryParser(_search_fields, _analyzer)
        parser.setDefaultOperator(parser.Operator.AND)
        try:
            hits = searcher.search(parser.parse(self._query_queue.get()))
            results = [document['id'] for index, document in hits]
        except JavaError:
            results = []
        self._results_queue.put(results)
        searcher.close()


class SearcherFactory(PythonThread):

    """Produces running Searcher threads.

    PythonThreads can only be started by the main program or other
    PythonThreads, so this PythonThread-based class creates and starts single-
    use Searcher threads.  This thread is created and started by the main
    program during TurboGears initialisation as a singleton.

    To get a Searcher thread, call the SearcherFactory instance.  The pass the
    query to the Search thread that is returned.

    """

    def __init__(self):
        """Constructor.  Initialises message queues and starts the thread."""
        PythonThread.__init__(self) # PythonThread is an old-style class
        self._request_queue = Queue()
        self._searcher_queue = Queue()
        self.start()

    def __call__(self):
        """Sends a request, then waits for and returns the resulting thread.

        The resulting thread is a running instance of the Searcher class.

        """
        self._request_queue.put('request')
        return self._searcher_queue.get()

    def run(self):
        """Listen for requests and create Searcher threads.

        If the request message is 'close', then shutdown.

        """
        while True:
            request = self._request_queue.get()
            assert request in ('request', 'close')
            if request == 'close':
                break
            self._searcher_queue.put(Searcher())

    def close(self):
        """Tell the thread to shutdown and then wait for it to do so."""
        self._request_queue.put('close')
        self.join()
