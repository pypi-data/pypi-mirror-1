# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

#==============================================================================
# turbolucene/__init__.py
#
# This is part of the TurboLucene project (http://dev.krys.ca/turbolucene/).
#
# Copyright (c) 2007 Krys Wilken <krys AT krys DOT ca>
#
# This software is licensed under the MIT license.  See the LICENSE file for
# licensing information.
#
#==============================================================================

"""Provides search functionality for TurboGears_ using PyLucene_.

This module uses PyLucene to do all the heavy lifting, but as a result this
module does some fancy things with threads.

PyLucene requires that all threads that use it must inherit from
``PythonThread``.  This means either patching CherryPy_ and/or TurboGears, or
having the CherryPy thread hand off the request to a ``PythonThread`` and, in
the case of searching, wait for the result.  The second method was chosen so
that a patched CherryPy or TurboGears does not have to be maintained.

The other advantage to the chosen method is that indexing happens in a separate
thread so the web request can return more quickly by not waiting for the
results.

The main disadvantage with PyLucene and CherryPy, however, is that *autoreload*
does not work with it.  You **must** disable it by adding
``autoreload.on = False`` to your ``dev.cfg``.

Configuration options
=====================

TurboLucene_ uses the following configuration options:

  **turbolucene.search_fields**:
    The list of fields that should be searched by default when a specific field
    is not specified.  (e.g. ``['id', 'title', 'text', 'categories']``)
    (Default: ``['id']``)
  **turbolucene.default_language**:
    The default language to use if a language is not given calling
    `add`/`update`/`search`/etc.  (Default: ``'en'``)
  **turbolucene.languages**:
    The list of languages to support.  This is a list of ISO language codes
    that you want to support in your application.  The languages must be
    supported by PyLucene and must be configured in the languages
    configuration file.  Currently the choice of languages that are possible
    out-of-the-box are : *Czech (cs)*, *Danish (da)*, *German (de)*, *Greek
    (el)*, *English (en)*, *Spanish (es)*, *Finnish (fi)*, *French (fr)*,
    *Italian (it)*, *Japanese (ja)*, *Korean (ko)*, *Dutch (nl)*, *Norwegian
    (no)*, *Portuguese (pt)*, *Brazilian (pt-br)*, *Russian (ru)*, *Swedish
    (sv)*, and *Chinese (zh)*.  (Default: ``[<default_language>]``)
  **turbolucene.default_operator**:
    The default search operator to use between search terms when non is
    specified.  (Default: ``'AND'``)  This must be a valid operator object from
    the ``PyLucene.MultiFieldQueryParser.Operator`` namespace.
  **turbolucene.optimize_days**:
    The list of days to schedule index optimization.  Index optimization cleans
    up and compacts the indexes so that searches happen faster.  This is a list
    of day numbers (Sunday = 1).  Optimization of all indexes will occur on
    those days.  (Default: ``[1, 2, 3, 4, 5, 6, 7]``, i.e. every day)
  **turbolucene.optimize_time**:
    A tuple containing the hour (24 hour format) and minute of the time to run
    the scheduled index optimizations.  (Default: ``(00, 00)``, i.e. midnight)
  **turbolucene.index_root**:
    The base path in which to store the indexes.  There is one index per
    supported language.  Each index is a directory.  Those directories will be
    sub-directories of this base path.  If the path is relative, it is
    relative to your project's root.  Normally you should not need to override
    this unless you specifically need the indexes to be located somewhere else.
    (Default: ``u'index'``)
  **turbolucene.languages_file**:
    The path to the languages configuration file.  The languages configuration
    file provides the configuration information for all the languages that
    *TurboLucene* supports.  Normally you should not need to override this.
    (Default: the ``u'languages.cfg'`` file in the `turbolucene` package)
  **turbolucene.languages_file_encoding**:
    The encoding of the languages file.  (Default: ``'utf-8'``)
  **turbolucene.stopwords_root**:
    The languages file can specify files that contain stopwords.  If a
    stopwords file path is relative, this path with be prepended to it.  This
    allows for all stopword files to be customized without needing to specify
    full paths for every one.  Normally you should not need to override this.
    (Default: the ``stopwords`` directory in the `turbolucene` package)
  **turbolucene.force_lock_release**:
    If this is set to True, then if TurboLucne has troubles opening an index,
    it will try to force the release of any write lock that may exist and try
    again.  The write lock is to prevent multiple processes writing to the
    same index at the same time, but if the TurboLucne-based project is killed,
    the lock gets left behind.  This setting let you override the default
    behaviour.  (Default: ``True`` in development and ``False`` in production)

All fields are optional, but at the minimum, you will likely want to specify
``turbolucene.search_fields``.

:See: `_load_language_data` for details about the languages configuration file.

:Warning: Do not forget to turn off *autoreload* in ``dev.cfg``.

:Requires: TurboGears_ and PyLucene_

.. _TurboGears: http://turbogears.org/
.. _PyLucene: http://pylucene.osafoundation.org/
.. _CherryPy: http://cherrypy.org/
.. _TurboLucene: http://dev.krys.ca/turbolucene/

:newfield api_version: API Version
:newfield revision: Revision

:group Objects to use in make_document: Document, Field, STORE, COMPRESS,
  TOKENIZED, UN_TOKENIZED
:group Public API: start, add, update, remove, search

"""

__author__ = 'Krys Wilken'
__contact__ = 'krys AT krys DOT ca'
__copyright__ = '(c) 2007 Krys Wilken'
__license__ = 'MIT'
__version__ = '0.2.2'
__api_version__ = '2.0'
__revision__ = '$Id: __init__.py 66 2007-05-17 01:55:31Z krys $'
__docformat__ = 'restructuredtext en'
__all__ = ['start', 'add', 'update', 'remove', 'search', 'Document', 'Field',
  'STORE', 'COMPRESS', 'TOKENIZED', 'UN_TOKENIZED']


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from Queue import Queue
from os.path import exists, join, isabs
from logging import getLogger
from atexit import register
import codecs

#---  Framework imports
from turbogears import scheduler, config
from configobj import ConfigObj
# PyLint does not like this setuptools voodoo, but it works.
from pkg_resources import resource_stream # pylint: disable-msg=E0611

#---  Third-party imports
import PyLucene
from PyLucene import (PythonThread, IndexModifier, JavaError, Term,
  IndexSearcher, MultiFieldQueryParser, FSDirectory)
# For use in make_document
from PyLucene import Document, Field


#---Globals--------------------------------------------------------------------

#: Default language to use if none is specified in `config`.
_DEFAULT_LANGUAGE = 'en'
# These are intentionally module-level globals, so C0103 does not apply.
#: Logger for this module
_log = getLogger('turbolucene') # pylint: disable-msg=C0103
#: This will hold the language support data read from file.
_language_data = None # pylint: disable-msg=C0103
#: This will hold the `_Indexer` singleton class.
_indexer = None # pylint: disable-msg=C0103
#: This will hold the `_SearcherFactory` singleton class.
_searcher_factory = None # pylint: disable-msg=C0103

#---  Convenience constants

#: Tells `Field` not to compress the field data
STORE = Field.Store.YES
#: Tells `Field` to compress the field data
COMPRESS = Field.Store.COMPRESS
#: Tells `Field` to tokenize and do stemming on the field data
TOKENIZED = Field.Index.TOKENIZED
#: Tells `Field` not to tokenize and do stemming on the field data
UN_TOKENIZED = Field.Index.UN_TOKENIZED


#---Functions------------------------------------------------------------------

def _load_language_data():
    """Load all the language data from the configured languages file.

    The languages configuration file can be set with the
    ``turbolucene.languages_file`` configuration option and it's encoding is
    set with ``turbolucene.languages_file_encoding``.

    Configuration file format
    =========================

    The languages file is an INI-type (ConfigObj_) file.  Each section is
    defined by an ISO language code (``en``, ``de``, ``el``, ``pt-br``, etc.).
    In each section the following keys are possible:

      **analyzer_class**:
        The PyLucene analyzer class to use for this language.  (e.g.
        ``SnowballAnalyzer``)  (Required)
      **analyzer_class_args**:
        Any arguments that should be passed to the analyzer class.  (e.g.
        ``Danish``)  (Optional)
      **stopwords**:
        A list of stopwords (words that do not get indexed) to pass to the
        analyzer class.  This is not normally used as ``stopwords_file`` is
        generally preferred.  (Optional)
      **stopwords_file**:
        The path to the file that contains the list of stopwords to pass to the
        analyzer class.  (e.g. ``stopwords_da.txt``)  (Optional)
      **stopwords_file_encoding**:
        The encoding of the stopwords file.  (e.g. ``windows-1252``)

    If neither ``stopwords`` or ``stopwords_file`` is defined for a language,
    then any stopwords that are used are determined automatically by the
    analyzer class' constructor.

    Example
    -------

    ::

      # German
      [de]
      analyzer_class = SnowballAnalyzer
      analyzer_class_args = German2
      stopwords_file = stopwords_de.txt
      stopwords_file_encoding = windows-1252

    :Exceptions:
      - `IOError`: Raised of the languages configuration file could not be
        opened.
      - `configobj.ParseError`: Raised if the languages configuration file is
        contains errors.

    :See:
      - `turbolucene` (module docstring) for details about configuration
        settings.
      - `_read_stopwords` for details about stopwords files.

    .. _ConfigObj: http://www.voidspace.org.uk/python/configobj.html

    """
    # Use of global here is intentional and necessary.  W0603 does not apply.
    global _language_data # pylint: disable-msg=W0603
    languages_file = config.get('turbolucene.languages_file', None)
    languages_file_encoding = config.get('turbolucene.languages_file_encoding',
      'utf-8')
    if languages_file:
        _log.info(u'Loading custom language data from "%s"' % languages_file)
    else:
        _log.info(u'Loading default language data')
        languages_file = resource_stream(__name__, u'languages.cfg')
    _language_data = ConfigObj(languages_file,
      encoding=languages_file_encoding, file_error=True, raise_errors=True)


def _schedule_optimization():
    """Schedule index optimization using the TurboGears scheduler.

    This function reads it's configuration data from
    ``turbolucene.optimize_days`` and ``turbolucene.optimize_time``.

    :Exceptions:
      - `TypeError`: Raised if ``turbolucene.optimize_time`` is invalid.

    :See: `turbolucene` (module docstring) for details about configuration
      settings.

    """
    optimize_days = config.get('turbolucene.optimize_days', range(1, 8))
    optimize_time = config.get('turbolucene.optimize_time', (00, 00))
    scheduler.add_weekday_task(_optimize, optimize_days, optimize_time)
    _log.info(u'Index optimization scheduled on %s at %s' % (unicode(
      optimize_days), unicode(optimize_time)))


def _get_index_path(language):
    """Return the path to the index for the given language.

    This function gets it's configuration data from ``turbolucene.index_root``.

    :Parameters:
      language : `str`
        An ISO language code.  (e.g. ``en``, ``pt-br``, etc.)

    :Returns: The path to the index for the given language.
    :rtype: `unicode`

    :See: `turbolucene` (module docstring) for details about configuration
      settings.

    """
    index_base_path = config.get('turbolucene.index_root', u'index')
    return join(index_base_path, language)


def _read_stopwords(file_path, encoding):
    """Read the stopwords from the given a stopwords file path.

    Stopwords are words that should not be indexed because they are too common
    or have no significant meaning (e.g. *the*, *in*, *with*, etc.)  They are
    language dependent.

    This function gets it's configuration data from
    ``turbolucene.stopwords_root``.

    If `file_path` is not an absolute path, then it will be appended to the
    path configured in ``turbolucene.stopwords_root``.

    Stopwords files are text files (in the given encoding), with one stopword
    per line.  Comments are marked by a ``|`` character.  This is for
    compatibility with the stopwords files found at
    http://snowball.tartarus.org/.

    :Parameters:
      file_path : `unicode`
        The path to the stopwords file to read.
      encoding : `str`
        The encoding of the stopwords file.

    :Returns: The list of stopwords from the file.
    :rtype: `list` of `unicode` strings

    :Exceptions:
      - `IOError`: Raised if the stopwords file could not be opened.

    :See: `turbolucene` (module docstring) for details about configuration
      settings.

    """
    stopwords_base_path = config.get('turbolucene.stopwords_root', None)
    if isabs(file_path) or stopwords_base_path:
        if not isabs(file_path):
            file_path = join(stopwords_base_path, file_path)
        _log.info(u'Reading custom stopwords file "%s"' % file_path)
        stopwords_file = codecs.open(file_path, 'r', encoding)
    else:
        _log.info(u'Reading default stopwords file "%s"' % file_path)
        stopwords_file = codecs.getreader(encoding)(resource_stream(__name__,
          join(u'stopwords', file_path)))
    stopwords = []
    for line in stopwords_file:
        # Stopword files can have comments after a '|' character on each line.
        # This is to support the stopword files that come from
        # http://snowball.tartarus.org/
        stopword = line.split(u'|')[0].strip()
        if stopword:
            stopwords.append(stopword)
    stopwords_file.close()
    return stopwords


def _analyzer_factory(language):
    """Produce an analyzer object appropriate for the given language.

    This function uses the data that was read in from the languages
    configuration file to determine and instantiate the analyzer object.

    :Parameters:
      language : `str` or `unicode`
        An ISO language code that is configured in the languages configuration
        file.

    :Returns: An instance of the configured analyser class for given language.
    :rtype: ``PyLucene.Analyzer`` sub-class

    :Exceptions:
      - `KeyError`: Raised if the given language is not configured or if the
        configuration for that language does not have a *analyzer_class* key.
      - `PyLucene.InvalidArgsError`: Raised if any of the parameters passed to
        the analyzer class are invalid.

    :See: `_load_language_data` for details about the language configuration
      file.

    """
    ldata = _language_data[language]
    args = (u'analyzer_class_args' in ldata and ldata[u'analyzer_class_args']
      or [])
    if not isinstance(args, list):
        args = [args]
    # Note: It seems that the <LANGUAGE>_STOP_WORDS class variables are not
    # exposed very often in PyLucene.  They are also not very complete anyway,
    # so I use stopwords from other sources.
    stopwords = []
    if u'stopwords' in ldata and ldata[u'stopwords']:
        stopwords = [ldata.stopwords]
    elif u'stopwords_file' in ldata and u'stopwords_file_encoding' in ldata:
        stopwords = [_read_stopwords(ldata[u'stopwords_file'],
          ldata[u'stopwords_file_encoding'])]
    # This function assumes that the stopwords parameter is always the last
    # argument to the analyzer constructor.  According to the Lucene docs, this
    # is true in all cases so far.
    args += stopwords
    # Use of *args here is deliberate and necessary, so W0142 does not apply.
    return getattr(PyLucene, ldata[ #pylint: disable-msg=W0142
      u'analyzer_class'])(*args)


def _stop():
    """Shutdown search engine threads."""
    _searcher_factory.stop()
    _indexer('stop')
    _log.info(u'Search engine stopped.')


def _optimize():
    """Tell the search engine to optimize it's index."""
    _indexer('optimize')


#---  Public API

def start(make_document, results_formatter=None):
    """Initialize and start the search engine threads.

    This function loads the language configuration information, starts the
    search engine threads, makes sure the search engine will be shutdown upon
    shutdown of TurboGears and starts the optimization scheduler to run at the
    configured times.

    The `make_document` and `results_formatter` parameters are
    callables.  Here are examples of how they should be defined:

    Example `make_document` function:
    ===================================

    .. python::

      def make_document(entry):
          '''Make a new PyLucene Document instance from an Entry instance.'''
          document = Document()
          # An 'id' string field is required.
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

    Example `results_formatter` function:
    =======================================

    .. python::

      def results_formatter(results):
          '''Return the results as SQLObject instances.

          Returns either an empty list or a SelectResults object.

          '''
          if results:
              return Entry.select_with_identity(IN(Entry.q.id, [int(id) for id
                in results]))

    :Parameters:
      make_document : callable
        `make_document` is a callable that will return a PyLucene `Document`
        object based on the object passed in to `add`, `update` or `remove`.
        The `Document` object must have at least a field called ``id`` that is
        a string.  This function operates inside a PyLucene ``PythonThread``.
      results_formatter : callable
        `results_formatter`, if provided, is a callable that will return
        a formatted version of the search results that are passed to it by
        `_Searcher.__call__`.  Generally the `results_formatter` will take the
        list of ``id`` strings that is passed to it and return a list of
        application-specific objects (like SQLObject_ instances, for example.)
        This function operates outside of any PyLucene ``PythonThread`` objects
        (like in the CherryPy thread, for example).  (Optional)

    :See:
      - `turbolucene` (module docstring) for details about configuration
        settings.
      - `_load_language_data` for details about the language configuration
        file.

    .. _SQLObject: http://sqlobject.org/

    """
    _load_language_data()
    # Use of global here is deliberate.  W0603 does not apply.
    global _indexer, _searcher_factory #pylint: disable-msg=W0603
    _indexer = _Indexer(make_document)
    _searcher_factory = _SearcherFactory(results_formatter)
    # Using atexit insted of call_on_shutdown so that tg-admin shell will also
    # shutdown properly.
    register(_stop)
    _schedule_optimization()
    _log.info(u'Search engine started.')


def add(object_, language=None):
    """Tell the search engine to add the given object to the index.

    This function returns immediately.  It does not wait for the indexer to be
    finished.

    :Parameters:
      `object_`
        This can be any object that ``make_document`` knows how to handle.
      language : `str`
        This is the ISO language code of the language of the object.  If
        `language` is given, then it must be on that was previously configured
        in ``turbolucene.languages``.  If `language` is not given, then
        the language configured in ``turbolucene.default_language`` will be
        used.  (Optional)

    :See:
      - `turbolucene` (module docstring) for details about configuration
        settings.
      - `start` for details about ``make_document``.

    """
    _indexer('add', object_, language)


def update(object_, language=None):
    """Tell the the search engine to update the index for the given object.

    This function returns immediately.  It does not wait for the indexer to be
    finished.

    :Parameters:
      `object_`
        This can be any object that ``make_document`` knows how to handle.
      language : `str`
        This is the ISO language code of the language of the object.  If
        `language` is given, then it must be on that was previously configured
        in ``turbolucene.languages``.  If `language` is not given, then
        the language configured in ``turbolucene.default_language`` will be
        used.  (Optional)

    :See:
      - `turbolucene` (module docstring) for details about configuration
        settings.
      - `start` for details about ``make_document``.

    """
    _indexer('update', object_, language)


def remove(object_, language=None):
    """Tell the search engine to remove the given object from the index.

    This function returns immediately.  It does not wait for the indexer to be
    finished.

    :Parameters:
      `object_`
        This can be any object that ``make_document`` knows how to handle.
      language : `str`
        This is the ISO language code of the language of the object.  If
        `language` is given, then it must be on that was previously configured
        in ``turbolucene.languages``.  If `language` is not given, then
        the language configured in ``turbolucene.default_language`` will be
        used.  (Optional)

    :See:
      - `turbolucene` (module docstring) for details about configuration
        settings.
      - `start` for details about ``make_document``.

    """
    _indexer('remove', object_, language)


def search(query, language=None):
    """Return results from the search engine that match the query.

    If a ``results_formatter`` function was passed to `start` then the results
    will be passed through the formatter before returning.  If not, the
    returned value is a list of strings that are the ``id`` fields of matching
    objects.

    :Parameters:
      query : `str` or `unicode`
        This is the search query to give to PyLucene.  All of Lucene's query
        syntax (field identifiers, wild cards, etc.) are available.
      language : `str`
        This is the ISO language code of the language of the object.  If
        `language` is given, then it must be on that was previously configured
        in ``turbolucene.languages``.  If `language` is not given, then
        the language configured in ``turbolucene.default_language`` will be
        used.  (Optional)

    :Returns: The results of the search.
    :rtype: iterable

    :See:
      - `start` for details about ``results_formatter``.
      - `turbolucene` (module docstring) for details about configuration
        settings.
      - http://lucene.apache.org/java/docs/queryparsersyntax.html for details
        about Lucene's query syntax.

    """
    return _searcher_factory()(query, language)


#---Classes--------------------------------------------------------------------

class _Indexer(PythonThread):

    """Responsible for updating and maintaining the search engine index.

    A single `_Indexer` thread is created to handle all index modifications.

    Once the thread is started, messages are sent to it by calling the instance
    with a task and an object, where the task is one of the following strings:

    - ``add``: Adds the object to the index.
    - ``remove``: Removes the object from the index.
    - ``update``: Updates the index of an object.

    and the object is any object that ``make_document`` knows how to handle.

    To properly shutdown the thread, send the ``stop`` task with `None` as the
    object.  (This is normally handled by the `turbolucene._stop` function.)

    To optimize the index, which can take a while, pass the ``optimize``
    task with `None` for the object.  (This is normally handled by the
    TurboGears scheduler as set up by `_schedule_optimization`.)

    :See: `turbolucene.start` for details about ``make_document``.

    :group Public API: __init__, __call__
    :group Threaded methods: run, _add, _remove, _update, _optimize, _stop

    """

    #---Public API

    def __init__(self, make_document):
        """Initialize the message queue and the PyLucene indexes.

        One PyLucene index is created/opened for each of the configured
        supported languages.

        This method uses the ``turbolucene.default_language``,
        ``turbolucene.languages`` and ``turbolucene.force_lock_release``
        configuration settings.

        :Parameters:
          make_document : callable
            A callable that takes the object to index as a parameter and
            returns an appropriate `Document` object.

        :Note: Instantiating this class starts the thread automatically.

        :See:
          - `turbolucene` (module docstring) for details about configuration
            settings.
          - `turbolucene.start` for details about ``make_document``.
          - `_get_index_path` for details about the directory location of each
            index.
          - `_analyzer_factory` for details about the analyzer used for each
            index.

        """
        PythonThread.__init__(self) # PythonThread is an old-style class
        self._make_document = make_document
        self._task_queue = Queue()
        self._indexes = {}
        default_language = config.get('turbolucene.default_language',
          _DEFAULT_LANGUAGE)
        default_force_lock_release = config.get('server.environment',
          'development').lower() == 'development' and True or False
        force_lock_release = config.get('turbolucene.force_lock_release',
          default_force_lock_release)
        # Create indexes
        languages = config.get('turbolucene.languages', [default_language])
        for language in languages:
            index_path = _get_index_path(language)
            analyzer = _analyzer_factory(language)
            create_path = not exists(index_path) and True or False
            try:
                self._indexes[language] = IndexModifier(index_path, analyzer,
                  create_path)
            except JavaError, error:
                if not error.getJavaException().getClass().getName(
                  ) == 'java.io.IOException' or not force_lock_release:
                    raise
                _log.warn('Error opening index "%s".  '
                  'turbolucene.force_lock_release is True, trying to force '
                  'lock release.' % index_path)
                FSDirectory.getDirectory(index_path, False).makeLock(
                  'write.lock').release()
                self._indexes[language] = IndexModifier(index_path, analyzer,
                  create_path)
        self.start()

    def __call__(self, task, object_=None, language=None):
        """Pass `task`, `object_` and `language` to the thread for processing.

        If `language` is `None`, then the default language configured in
        ``turbolucene.default_language`` is used.

        If `task` is ``stop``, then the `_Indexer` thread is shutdown and this
        method will wait until the shutdown is complete.

        :Parameters:
          task : `str`
            The task to perform.
          `object_`
            Any object that ``make_document`` knows how to handle. (Default:
            `None`)
          language : `str`
            The ISO language code of the language of the object.  This
            specifies which PyLucene index to use.

        :See:
          - `turbolucene` (module docstring) for details about configuration
            settings.
          - `turbolucene.start` for details about ``make_document``.

        """
        if not language:
            language = config.get('turbolucene.default_language',
              _DEFAULT_LANGUAGE)
        self._task_queue.put((task, object_, language))
        if task == 'stop':
            self.join()

    #---Threaded methods

    def run(self):
        """Main thread loop to do dispatching based on messages in the queue.

        This method expects that the queue will contain 3-tuples in the form of
        (task, object, language), where task is one of ``add``, ``update``,
        ``remove``, ``optimize`` or ``stop``,  entry is any object that
        ``make_document`` can handle or `None` in the case of ``optimize`` and
        ``stop``, and language is the ISO language code of the indexer.

        If the task is ``stop``, then the thread shuts down.

        :Note: This method is run in the thread.

        :See:
          - `_add`, `_update`, `_remove`, `_optimize` and `_stop` for details
            about each respective task.
          - `turbolucene.start` for details about ``make_document``.

        """
        while True:
            task, object_, language = self._task_queue.get()
            method = getattr(self, '_' + task)
            if task in ('optimize', 'stop'):
                method()
            else:
                method(object_, language)
            if task == 'stop':
                break
            self._indexes[language].flush() # This is essential.

    def _add(self, object_, language, document=None):
        """Add a new object to the index.

        If `document` is not provided, then this method passes the object off
        to ``make_document`` and then indexes the resulting `Document` object.
        Otherwise it just indexes the `document` object.

        :Parameters:
          `object_`
            The object to be indexed.  It will be passed to ``make_document``
            (unless `document` is provided).
          language : `str`
            The ISO language code of the indexer to use.
          document : `Document`
            A pre-built `Document` object for the given object, if it exists.
            This is used internally by `_update`.  (Default: `None`)

        :Note: This method is run in the thread.

        :See: `turbolucene.start` for details about ``make_document``.

        """
        if not document:
            document = self._make_document(object_)
        _log.info(u'Adding object "%s" (id %s) to the %s index.' % (unicode(
          object_), document['id'], language))
        self._indexes[language].addDocument(document)

    def _remove(self, object_, language, document=None):
        """Remove an object from the index.

        If `document` is not provided, then this method passes the object off
        to ``make_document`` and then removes the resulting `Document` object
        from the index.  Otherwise it just removes the `document` object.

        :Parameters:
          `object_`
            The object to be removed from the index.  It will be passed to
            ``make_document`` (unless `document` is provided).
          language : `str`
            The ISO language code of the indexer to use.
          document : `Document`
            A pre-built `Document` object for the given object, if it exists.
            This is used internally by `_update`.  (Default: `None`)

        :Note: This method is run in the thread.

        :See: `turbolucene.start` for details about ``make_document``.

        """
        if not document:
            document = self._make_document(object_)
        _log.info(u'Removing object "%s" (id %s) from %s index.' % (unicode(
          object_), document['id'], language))
        self._indexes[language].deleteDocuments(Term('id', document['id']))

    def _update(self, object_, language):
        """Update an object in the index by replacing it.

        This method updates the index by removing and then re-adding the
        object.

        :Parameters:
          `object_`
            The object to update in the index.  It will be passed to
            ``make_document`` and the resulting `Document` object will be
            updated.
          language : `str`
            The ISO language code of the indexer to use.

        :Note: This method is run in the thread.

        :See:
          - `_remove` and `_add` for details about the removal and
            re-addition.
          - `turbolucene.start` for details about ``make_document``.

        """
        document = self._make_document(object_)
        self._remove(object_, language, document)
        self._add(object_, language, document)

    def _optimize(self):
        """Optimize all of the indexes.  This can take a while.

        :Note: This method is run in the thread.

        """
        _log.info(u'Optimizing indexes.')
        for index in self._indexes.values():
            index.optimize()
        _log.info(u'Indexes optimized.')

    def _stop(self):
        """Shutdown all of the indexes.

        :Note: This method is run in the thread.

        """
        for index in self._indexes.values():
            index.close()


class _Searcher(PythonThread):

    """Responsible for searching an index and returning results.

    `_Searcher` threads are created for each search that is requested.  After
    the search is completed, the thread dies.

    To search, a `_Searcher` class is instantiated and then called with the
    query and the ISO language code for the index to search.  It returns the
    results as a list of object id strings unless ``results_formatter`` was
    provided.  If it was, then the list of id strings are passed to
    ``results_formatter`` to process and it's results are returned.

    The thread is garbage collected when it goes out of scope.

    The catch to all this is that a CherryPy thread cannot directly instantiate
    a `_Searcher` thread because of PyLucene restrictions.  So to get around
    that, see the `_SearcherFactory` class.

    :See: `turbolucene.start` for details about ``results_formatter``.

    :group Public API: __init__, __call__
    :group Threaded methods: run

    """

    #---Public API

    def __init__(self, results_formatter):
        """Initialize message queues and start the thread.

        :Note: The thread is started as soon as the class is instantiated.

        """
        PythonThread.__init__(self) # PythonThread is an old-style class
        self._results_formatter = results_formatter
        self._query_queue = Queue()
        self._results_queue = Queue()
        self.start()

    def __call__(self, query, language=None):
        """Send `query` and `language` to the thread, wait and return results.

        If `language` is `None`, then the default language configured in
        ``turbolucene.default_language`` is used.

        :Parameters:
          query : `str` or `unicode`
            The search query to give to PyLucene.  All of Lucene's query
            syntax (field identifiers, wild cards, etc.) are available.
          language : `str`
            The ISO language code of the indexer to use.

        :Returns: An iterable of id field strings that match the query or the
          results produced by ``results_formatter`` if it was provided.
        :rtype: iterable

        :See:
          - `turbolucene` (module docstring) for details about configuration
            settings.
          - `turbolucene.start` for details about ``results_formatter``.
          - http://lucene.apache.org/java/docs/queryparsersyntax.html for
            details about Lucene's query syntax.

        """
        if not language:
            language = config.get('turbolucene.default_language',
              _DEFAULT_LANGUAGE)
        self._query_queue.put((query, language))
        results = self._results_queue.get()
        # The join is causing a segfault and I don't know why.  In theory the
        # join should not be necessary, but I thought it good practice to
        # include it.  Apparently I am wrong.
##        self.join()
        if self._results_formatter:
            return self._results_formatter(results)
        return results

    #---Threaded methods

    def run(self):
        """Search the language index for the query and send back the results.

        The results is an iterable of id field strings that match the query.

        This method uses the ``turbolucene.search_fields`` configuration
        setting for the default fields to search if none are specified in the
        query itself,  and ``turbolucene.default_operator`` for the default
        operator to use when joining terms.

        :Exceptions:
          - `AttributeError`: Raised when the configured default operator is
            not valid.

        :Note: This method is run in the thread.

        :Note: The thread dies after one search.

        :See:
          - `turbolucene` (module docstring) for details about configuration
            settings.
          - `_get_index_path` for details about the directory location of the
            index.
          - `_analyzer_factory` for details about the analyzer used for the
            index.
          - http://lucene.apache.org/java/docs/queryparsersyntax.html for
            details about Lucene's query syntax.

        """
        query, language = self._query_queue.get()
        searcher = IndexSearcher(_get_index_path(language))
        search_fields = config.get('turbolucene.search_fields', ['id'])
        parser = MultiFieldQueryParser(search_fields, _analyzer_factory(
          language))
        default_operator = getattr(parser.Operator, config.get(
          'turbolucene.default_operator', 'AND').upper())
        parser.setDefaultOperator(default_operator)
        try:
            hits = searcher.search(parser.parse(query))
            results = [document['id'] for _, document in hits]
        except JavaError:
            results = []
        self._results_queue.put(results)
        searcher.close()


class _SearcherFactory(PythonThread):

    """Produces running `_Searcher` threads.

    ``PythonThread`` threads can only be started by the main program or other
    ``PythonThread`` threads, so this ``PythonThread``-based class creates and
    starts single-use `_Searcher` threads.  This thread is created and started
    by the main program during TurboGears initialization as a singleton.

    To get a `_Searcher` thread, call the `_SearcherFactory` instance.  Then
    pass the query to the `_Searcher` thread that was returned.

    :group Public API: __init__, __call__, stop
    :group Threaded methods: run

    """

    #---Public API

    def __init__(self, *searcher_args, **searcher_kwargs):
        """Initialize message queues and start the thread.

        :Note: The thread is started as soon as the class is instantiated.

        """
        PythonThread.__init__(self) # PythonThread is an old-style class
        self._searcher_args = searcher_args
        self._searcher_kwargs = searcher_kwargs
        self._request_queue = Queue()
        self._searcher_queue = Queue()
        self.start()

    def __call__(self):
        """Send a request for a running `_Searcher` class, then return it.

        :Returns: A running instance of the `_Searcher` class.
        :rtype: `_Searcher`

        """
        self._request_queue.put('request')
        return self._searcher_queue.get()

    def stop(self):
        """Stop the `_SearcherFactory` thread."""
        self._request_queue.put('stop')
        self.join()

    #---Threaded methods

    def run(self):
        """Listen for requests and create `_Searcher` classes.

        If the request message is ``stop``, then the thread will be shutdown.

        :Note: This method is run in the thread.

        """
        while True:
            request = self._request_queue.get()
            if request == 'stop':
                break
            # * and ** are used here for simplicity and transparency.
            self._searcher_queue.put(_Searcher( # pylint: disable-msg=W0142
              *self._searcher_args, **self._searcher_kwargs))
