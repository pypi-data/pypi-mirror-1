# (C) Copyright 2007 Nuxeo SAS <http://nuxeo.com>
# Author: bdelbosc@nuxeo.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#
"""PLUSH kind of PyLUceneSHell.

$Id: plush.py 51139 2007-02-19 21:22:12Z bdelbosc $
"""
import sys
import os
import re
from sre_compile import error as RegexError
from datetime import datetime
import readline
from time import time
from cmd import Cmd

from PyLucene import FrenchAnalyzer
from PyLucene import GermanAnalyzer
from PyLucene import KeywordAnalyzer
from PyLucene import SimpleAnalyzer
from PyLucene import StandardAnalyzer
from PyLucene import StopAnalyzer
from PyLucene import WhitespaceAnalyzer
from PyLucene import QueryParser, IndexSearcher, FSDirectory
from PyLucene import IndexReader, Sort, JavaError
from PyLucene import VERSION, LUCENE_VERSION
from PyLucene import IndexWriter, Field, Document, RAMDirectory

from version import __version__

#------------------------------------------------------------
# utils
#
def truncStr(text, size=72):
    """Truncate a string."""
    if not text:
        return ''
    if not size or len(text) < size:
        return text
    else:
        return text[:size] + '...'

def guessEncoding():
    """Guess the cmd encoding."""
    encoding = 'iso-8859-15'
    lang = os.getenv('LC_ALL', None)
    if not lang:
        lang = os.getenv('LANG')
    if lang and 'utf-8' in lang.lower():
        encoding = 'utf-8'
    return encoding



class StringReader(object):
    """Class for analyzer input."""
    def __init__(self, u_text):
        super(StringReader, self).__init__()
        self.unicodeText = unicode(u_text)

    def read(self, length=-1):
        """Read."""
        text = self.unicodeText
        if text is None:
            return u''
        if length == -1 or length >= len(text):
            self.unicodeText = None
            return text
        text = text[:length]
        self.unicodeText = self.unicodeText[length:]
        return text

    def close(self):
        """Close"""
        pass

#------------------------------------------------------------
# Base class
#
class PlushBase:
    """Base class."""

    def __init__(self, store_dir=None, verbose=False):
        self.verbose = verbose
        self.store_path = None
        self.searcher = None
        self.index_reader = None
        self.directory = None
        self.analyzers = {}
        self.initAnalyzers()
        self.default_analyzer_id = 'Simple'
        self.fields = []
        self._connected = False
        if store_dir:
            self.openStore(store_dir)

    def __del__(self):
        self.closeStore()
        self._connected = False

    def initDummyStore(self, directory):
        """Open a dummy ramdirectory for testing."""
        writer = IndexWriter(directory, SimpleAnalyzer(), True)
        doc = Document()
        doc.add(Field("name", 'dummy.txt', Field.Store.YES,
                      Field.Index.UN_TOKENIZED))
        doc.add(Field("path", '/path/to/dummy.txt', Field.Store.YES,
                      Field.Index.UN_TOKENIZED))
        doc.add(Field("contents", "foo dummy bar", Field.Store.YES,
                      Field.Index.TOKENIZED))
        writer.addDocument(doc)
        writer.optimize()
        writer.close()

    def openStore(self, store_dir):
        """Open a lucene store."""
        if self._connected:
            self.closeStore()
        if store_dir == 'dummy':
            directory = RAMDirectory()
            self.initDummyStore(directory)
            store_path = store_dir
        else:
            store_path = os.path.abspath(store_dir)
            try:
                directory = FSDirectory.getDirectory(store_path, False)
            except JavaError:
                print "Error: %s Not found." % store_path
                return
        try:
            self.searcher = IndexSearcher(directory)
        except JavaError:
            print "Error: '%s' is not a valid lucene store." % store_path
            return
        print 'Opening store: %s' % store_path
        self.directory = directory
        self.store_path = store_path
        self.index_reader = IndexReader.open(directory)
        self.fields = self.getFieldNames()
        self.fields.sort()
        self._connected = True


    def closeStore(self):
        """Close a lucene store."""
        if self.searcher is not None:
            if self.verbose:
                print "Close searcher."
            self.searcher.close()
            self.directory = None
            self.searcher = None
            self.index_reader = None
            self.fields = []
            self.store_path = None
        self._connected = False

    def maxDoc(self):
        """Maximum doc number."""
        return self.index_reader.maxDoc()

    def numDocs(self):
        """Number of docs in the store."""
        return self.index_reader.numDocs()

    def getFieldNames(self):
        """Return all index name from the index reader."""
        if VERSION.startswith('1.9'):
            return self.index_reader.getFieldNames()
        return self.index_reader.getFieldNames(IndexReader.FieldOption.ALL)

    def getFields(self, doc_num=None):
        """Return fields of a doc."""
        if doc_num is None:
            doc_num = self.maxDoc() - 1
        doc = self.index_reader.document(doc_num)
        return doc.fields()

    def getDoc(self, doc_num=None):
        """Return a lucene doc."""
        if doc_num is None:
            doc_num = self.maxDoc() - 1
        return self.index_reader.document(doc_num)

    def getFieldInfos(self, doc_num=None):
        """Return fields description.

        [(name, stored, index, token, binary, compressed), ...]"""
        fields = []
        doc = self.getDoc(doc_num)
        for name in self.fields:
            field = doc.getField(name)
            if field:
                fields.append((field.name(), field.isStored(),
                               field.isIndexed(),
                               field.isTokenized(), field.isBinary(),
                               field.isCompressed(), field.stringValue()))
            else:
                fields.append((name, False, False, False, False, False,
                               'N/A'))
        return fields

    def search(self, command, field_id="contents", sort_on=None,
               sort_order=False, analyzer_id=None):
        """Do the lucene search."""
        analyzer = self.getAnalyzer(analyzer_id)
        try:
            if VERSION.startswith('1.9'):
                query = QueryParser.parse(command, field_id, analyzer)
            else:
                query = QueryParser(field_id, analyzer).parse(command)
        except JavaError:
            print "Error: Lucene cannot parse this query."
            return None
        if sort_on:
            return self.searcher.search(query, Sort(sort_on, sort_order))
        return self.searcher.search(query)

    def getTermFreqs(self, field=None, max_term=None, pattern=None):
        """Return a list of (number of occurence, word) for the field."""
        item = self.index_reader.terms()
        min_freq = 0
        freqs = []
        if max_term:
            limit = max_term
        else:
            limit = 1000
        if pattern is not None:
            try:
                pat = re.compile(pattern)
            except RegexError:
                print "Error: '%s' is an invalid regex" % pattern
                return []
        while(item.next()):
            term = item.term()
            if field and term.field() != field:
                continue
            word = term.text()
            freq = item.docFreq()
            if pattern is not None and not pat.search(word):
                continue
            if len(freqs) >= limit and freq < min_freq:
                continue
            freqs.append((-1 * freq, word))
            freqs.sort()
            if len(freqs) > limit:
                freqs.pop()
            min_freq = freqs[0][0]

        freqs = [(-1*freq, word) for freq, word in freqs]
        return freqs

    def initAnalyzers(self):
        """Init all analyzer."""
        self.analyzers['French'] = FrenchAnalyzer()
        self.analyzers['German'] = GermanAnalyzer()
        self.analyzers['Keyword'] = KeywordAnalyzer()
        self.analyzers['Simple'] = SimpleAnalyzer()
        self.analyzers['Stop'] = StopAnalyzer()
        self.analyzers['Standard'] = StandardAnalyzer()
        self.analyzers['Whitespace'] = WhitespaceAnalyzer()
        nxlucene_home = os.getenv('NXLUCENE_HOME', None)
        if nxlucene_home:
            # point to http://svn.nuxeo.org/pub/NXLucene/trunk/src/nxlucene
            nxlucene_home = os.path.normpath(nxlucene_home)
            sys.path.append(nxlucene_home)
            try:
                from analysis import analyzers_map
            except ImportError:
                print "Error: Invalid NXLUCENE_HOME %s" % nxlucene_home
                return
            for key, value in analyzers_map.items():
                self.analyzers['nx' + key] = value
            print "NXLucene analyzers loaded."

    def getAnalyzer(self, analyzer_id=None):
        """Return an analyzer or default."""
        if analyzer_id is None:
            analyzer_id = self.default_analyzer_id
        return self.analyzers.get(analyzer_id)

    def displayAnalyzedQuery(self, text, field_name, analyzer_id=None):
        """Print analyzed tokens."""
        analyzer = self.getAnalyzer(analyzer_id)
        tokens = [token.termText() for token in analyzer.tokenStream(
            field_name, StringReader(text))]
        print "  %s analyzer tokens: %s" % (
            analyzer_id or self.default_analyzer_id,
            ", ".join(tokens) )

#------------------------------------------------------------
# mixin Cmd Plush
#
class Plush(Cmd, PlushBase):
    """Mixin plush and cmd class."""

    intro = """Welcome to Plush %s, a Lucene interactive terminal.
Using PyLucene %s and Lucene %s.

  Type: \open [INDEX_PATH]    to open a lucene store
        \?                    for help
        \q or ^D              to quit.""" % (__version__,
                                             VERSION, LUCENE_VERSION)
    plush_attr = ('limit', 'select', 'default_field', 'sort_on',
                  'waterline', 'analyzer', 'trunc_size')
    default_field = 'contents'
    select = 'name path'
    limit = 5
    sort_on = ''
    analyzer = 'Simple'
    history_path = '~/plush_history'
    waterline = ''
    trunc_size = 150

    def __init__(self, store_dir, verbose=False):
        Cmd.__init__(self)
        PlushBase.__init__(self, store_dir, verbose)
        self.cmd_encoding = guessEncoding()
        self.prompt = 'plush> '
        self.is_query = True
        self.history_path = os.path.expanduser('~/.plush_history')
        self.query_hist = []
        if os.path.exists(self.history_path):
            readline.read_history_file(self.history_path)

    def checkStore(self):
        """Warn if there is no open store."""
        if not self._connected:
            print "Error: You must open a store first.",
            print "Type: \? for more information."
        return self._connected

    def _getResultFieldIds(self):
        """Return list of selected field ids."""
        return filter(None, self.select.split())

    def _getSortOption(self, message=None):
        """Parse a sort_on value return (sort_on, sort_order)."""
        if message is None:
            tmp = self.sort_on.split()
        else:
            tmp = message.split()
        if not tmp:
            return None, False
        sort_on = tmp[0]
        sort_order = tmp[-1]
        if not sort_on.strip():
            sort_on = None
        if 'desc' in sort_order.lower():
            sort_order = True
        else:
            sort_order = False
        return sort_on.strip(), sort_order

    # commands ----------------------------------------------
    def do_echo(self, message):
        """Echo command."""
        print message
        return 0

    def help_help(self):
        """help"""
        print "?"

    def do_quit(self, message):
        """\q[uit]
        Quit without warning."""
        readline.write_history_file(self.history_path)
        print "Bye"
        return 1
    do_exit = do_quit
    do_q = do_quit

    def do_describe_store(self, message):
        """\d[escribe_store]
        General information about the store."""
        if not self.checkStore():
            return
        nb_docs = self.numDocs()
        max_doc = self.maxDoc()
        directory = self.directory
        print "Directory info"
        print "--------------"
        print "* Directory path             : %s" % self.store_path
        print "* Directory current version  : %s" % (
            IndexReader.getCurrentVersion(directory))
        print "* Number of docs             : %s (max doc num: %s)" % (
            nb_docs, max_doc)
        print "* Number of fields           : %d" % len(self.fields)
        print "* Number of terms            :",
        terms = self.index_reader.terms()
        nb_terms = 0
        while terms.next():
            nb_terms += 1
        terms.close()
        print nb_terms
        try:
            last_modified = datetime.fromtimestamp(
                IndexReader.lastModified(directory)/1000.0)
            last_modified = last_modified.isoformat()
        except ValueError:
            last_modified = "Unknown"
        print "* Index last modified        : %s" % last_modified
        print "* Index status               :",
        if IndexReader.isLocked(directory):
            print "LOCKED"
        else:
            print "unlocked"
        print "* Has deletions              :",
        if self.index_reader.hasDeletions():
            print "YES"
        else:
            print "no"
        print "* Directory implementation   : %s" % (
            directory.getClass().getName())
    do_d = do_describe_store

    def do_describe_indexes(self, message):
        """\describe_indexes [DOC_NUM] or \di [DOC_NUM]
        Describe indexes for DOC_NUM."""
        if not self.checkStore():
            return
        print "Index info"
        print "----------"
        max_doc = self.maxDoc()
        num_doc = max_doc - 1
        if message:
            try:
                num_doc = int(message)
            except ValueError:
                print "Error: Invalid value for doc num"
            if num_doc < 0 or num_doc >= max_doc:
                print "Error: Invalid doc num"
                num_doc = max_doc - 1
        if self.index_reader.isDeleted(num_doc):
            print "Error: doc num %d is deleted." % num_doc
            return
        fields = self.getFieldInfos(num_doc)
        print "Found %d fields for doc #%d:" % (len(fields), num_doc)
        for field in fields:
            print "* %-27s  %s %s %s %s %s" % (
                field[0],
                field[1] and 'Stored' or '      ',
                field[2] and 'Indexed' or '       ',
                field[3] and 'Tokenized' or '        ',
                field[4] and 'Binary' or '      ',
                field[5] and 'Compressed' or '         ')
    do_di = do_describe_indexes

    def do_view(self, message):
        """\\v[iew] [DOC_NUM [FIELD_PATTERN]]
        View values of index fields that matches PATTERN for DOC_NUM

        ex:
        \\v 123
        \\v 123 name|path"""
        if not self.checkStore():
            return
        nb_docs = self.maxDoc()
        num_doc = nb_docs - 1
        pattern = None
        if message:
            words = message.split(' ', 1)
            num_doc = None
            pattern = None
            if len(words) >= 1:
                num_doc = words[0].strip()
            if len(words) == 2:
                pattern = words[1].strip()
            try:
                num_doc = int(num_doc)
            except ValueError:
                print "Error: Invalid value for doc num"
            if num_doc < 0 or num_doc >= nb_docs:
                print "Error: Invalid doc num"
                num_doc = nb_docs -1
        if pattern:
            try:
                pat = re.compile(pattern)
            except RegexError:
                print "Error: '%s' is an invalid regex" % pattern
                pattern = None

        if self.index_reader.isDeleted(num_doc):
            print "doc num %d is deleted." % num_doc
            return

        trunc_size = self.trunc_size
        fields = self.getFieldInfos(num_doc)
        print "Found %d fields for doc #%d" % (len(fields), num_doc)
        for field in fields:
            if pattern is not None and not pat.search(field[0]):
                continue
            print "%-25s  %s %s %s %s %s: %s" % (field[0],
                                                 field[1] and 'S' or ' ',
                                                 field[2] and 'I' or ' ',
                                                 field[3] and 'T' or ' ',
                                                 field[4] and 'B' or ' ',
                                                 field[5] and 'C' or ' ',
                                                 truncStr(field[6],
                                                          trunc_size))
    do_v = do_view

    def do_open(self, message):
        """\open [INDEX_PATH]
        Open a lucene store.

        ex:
        \open /path/to/the/lucene/index"""
        self.openStore(message)

    def do_close(self, message):
        """\close
        Close the current store."""
        self.closeStore()

    def do_set(self, message):
        """\set [NAME [VALUE]]
        Set internal variable, or list all if no parameters.

        Where NAME can be:
        limit          limit the result lists.
        default_field  default index field use for searching.
        select         fields to display in the result list.
        sort_on        fields used to sort the result list.
        waterline      post filter result list and remove doc_num < waterline.
        analyzer       select one of the lucene analyzer : Whitespace, Keyword,
                       German, Stop, French, Standard, Simple.
        ex:
        \set limit 10
        \set default_field SearchableText
        \set select Title Description uid
        \set sort_on Date_Sort DESC
        \set waterline 123
        \set analyzer Keyword
        """
        words = message.split(' ', 1)
        key = None
        value = None
        if len(words) >= 1:
            key = words[0].strip()
        if len(words) == 2:
            value = words[1].strip()
        if not key:
            for key in self.plush_attr:
                print "  %s = %s" % (key, getattr(self, key))
            return
        if key not in self.plush_attr:
            print "Error: '%s' is not a valid key." % key
            print "       Valid keys are: %s." % ', '.join(self.plush_attr)
            return
        if not value:
            print "  %s = %s" % (key, getattr(self, key, 'unset ?'))
            return
        if key in ('limit', 'waterline', 'trunc_size'):
            try:
                value = int(value)
            except ValueError:
                print "Error: Invalid value an integer expected."
                return
        if key == 'sort_on':
            field_name, order = self._getSortOption(value)
            if field_name not in self.fields:
                print "No field %s in the store." % field_name
                return
            a_doc = self.getDoc()
            field = a_doc.getField(field_name)
            if field is not None and field.isTokenized():
                print "It is not possible to sort on a tokenized field"
                return
        if key == 'analyzer':
            if value not in self.analyzers.keys():
                print "Error: Invalid analyzer."
                print "       Possible values are: %s" % (
                    ', '.join(self.analyzers.keys()),)
                return
        setattr(self, key, value)
        print "  %s key setted." % key
        return 0

    def complete_set(self, *args):
        """Completion for the set cmd."""
        if 'analyzer' in args[1]:
            completions = self.analyzers.keys()
        else:
            completions = self.plush_attr
        return [attr for attr in completions if attr.startswith(args[0])]

    def do_unset(self, message):
        """\unset [NAME]
        Unset (delete) internal variable."""
        if message in self.plush_attr:
            print "  Unsetted"
            setattr(self, message, '')

    def complete_unset(self, *args):
        """Completion for the set cmd."""
        return [attr for attr in self.plush_attr if attr.startswith(args[0])]

    def do_nuxset(self, message):
        """Setup default variable for nxlucene."""
        self.default_field = "SearchableText"
        self.select = "Title uid Description"
        #self.sort_on = "Title_Sort ASC"

    def do_term(self, message):
        """\\term [INDEX_NAME|*] [REGEX]
        Display top term frequency for INDEX_NAME that match the REGEX.

        term
        term name
        term contents foo
        term contents ^f?o
        term * foo
        """
        if not self.checkStore():
            return
        words = message.split(' ', 1)
        field = words[0].strip()
        if len(words) == 2:
            pattern = words[1].strip()
        else:
            pattern = None
        if pattern and field == '*':
            field = None
        if field and field not in self.fields:
            print "No '%s' field in the current index." % field
            return
        print "Top %d term occurences for field '%s' matching '%s'." % (
            self.limit, field and field or '*', pattern and pattern or '*')
        items = self.getTermFreqs(field, self.limit, pattern)
        if not items:
            print "No match."
            return
        print "occurences term"
        print "---------- ----"
        for freq, term in items:
            print "  %8d %s" % (freq, term)
        print "---------- ----"

    def do_history(self, message):
        """\history
        Query history."""
        for (analyzer, query, sort_on, hits, delta) in self.query_hist:
            print "* query   : %s" % query
            if sort_on:
                print "  sort on : %s" % sort_on
            print "  hits    : %d" % hits,
            print "  elapsed : %.3fs" % delta,
            print "  analyzer: %s" % analyzer



    def default(self, line):
        """A lucene query."""
        if not self.checkStore():
            return
        if not self.is_query:
            print "Error: Invalid command."
            return 0
        print "Searching: %s" % line
        print "------------------------------------"
        print "  Default search index: %s" % self.default_field
        if self.sort_on:
            print "  Sort on %s" % self.sort_on
        line = unicode(line, self.cmd_encoding)
        sort_on, sort_order = self._getSortOption()
        self.displayAnalyzedQuery(line, self.default_field, self.analyzer)
        t_start = time()
        hits = self.search(line, field_id=self.default_field,
                           sort_on=sort_on, sort_order=sort_order,
                           analyzer_id=self.analyzer)
        if hits is None:
            return 0
        delta = time() - t_start
        nb_hits = hits.length()
        print "  Found %s matching document(s) in %.3fs" % (nb_hits, delta)
        if nb_hits:
            print
        i = 0
        limit = self.limit
        waterline = self.waterline
        count = 0
        result_fields = self._getResultFieldIds()
        for i, doc in hits:
            doc_num = hits.id(i)
            if waterline and doc_num < waterline:
                continue
            if limit and count > limit:
                print "----- LIMIT %d ----" % self.limit
                break
            print "* %2.2d) score: %.2f, doc_num: %s" % (count, hits.score(i),
                                                         hits.id(i))
            for field in result_fields:
                print '  %s: %s' % (field, truncStr(doc.get(field),
                                                    self.trunc_size))
            print
            count += 1
        if count:
            print "  Found %s matching document(s) in %.3fs" % (nb_hits, delta)
            self.query_hist.append((self.analyzer, line, self.sort_on,
                                    nb_hits, delta))
        if waterline:
            print "%d document with doc_num >= %d" % (count, waterline)
        return 0


    def cmdline(self, line):
        """do cmd line.

        used by doc test."""
        line = self.precmd(line)
        stop = self.onecmd(line)
        stop = self.postcmd(stop, line)


    # Cmd override to handle backslash cmd ------------------
    doc_header = "Documented commands (type \help <topic>):"
    def emptyline(self):
        """Called when an empty line is entered in response to the prompt."""
        pass

    def precmd(self, line):
        """Escaping backslash cmd"""
        if line.startswith('\\'):
            self.is_query = False
            return line[1:]
        self.is_query = True
        return line

    def parseline(self, line):
        """Patch to handle backslash cmd and EOF"""
        if not self.is_query:
            return Cmd.parseline(self, line)
        if line == 'EOF':
            print "^D"
            return ('quit', None, line)
        return (None, None, line)

    def complete(self, text, state):
        """Patch to handle backslash cmd
        Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
            import readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            if not line.startswith('\\'):
                return None
            line = line[1:]
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            if begidx > 0:
                cmd, args, foo = self.parseline(line)
                if cmd == '':
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                    except AttributeError:
                        compfunc = self.completedefault
            else:
                compfunc = self.completenames
            self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None


class PlushProg:
    """Plush prog."""
    store = None
    def __init__(self):
        if len(sys.argv) > 1:
            self.store = sys.argv[1]

    def run(self):
        """Run"""
        plush = Plush(self.store)
        plush.cmdloop()


if __name__ == '__main__':
    prog = PlushProg()
    prog.run()
