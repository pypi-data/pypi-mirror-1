# $Id$
#
"""
Iterators are used to make variable substitutions
"""
import csv

import logging
log = logging.getLogger('modipy')

from twisted.enterprise import adbapi
from twisted.internet import defer

from namespace import create_namespace

class Iterator:
    """
    A ModiPy Iterator contains a series of Namespaces that
    are iterated over one by one for use in variable substitutions.
    """
    def __init__(self, name):
        self.name = name
        self.iterlist = []

    def __iter__(self):
        """
        Really must define this somehow.
        """
        return self.iterlist.__iter__()

    def __len__(self):
        return len(self.iterlist)

    def next(self):
        return self.iterlist.next()

    def append(self, item):
        self.iterlist.append(item)

    def load_config(self, ignored):
        """
        Asynchronously load the iterator configuration when required.
        """
        pass

class CSVIterator(Iterator):
    """
    A CSVIterator uses a .csv formatted file containing a list
    of named columns, and their values. The .csv should adhere
    to the following format:

    The first line should contain a list of keywords, in order,
    separated by commas (obviously, as it's a CSV file).

    All subsequent lines are the values for the keywords in the
    first line.
    """

    def __init__(self, name, node):
        Iterator.__init__(self, name)

        try:
            self.filepath = node.attrib['file']

        except KeyError:
            raise ValueError("CSV Iterator has no 'file' attribute defined")
        pass

    def load_config(self, ignored=None):
        """
        Load a CSV formatted file into myself.
        """
        self.iterlist = csv.DictReader(open(self.filepath, "rb"))

class DictConnectionPool(adbapi.ConnectionPool):
    """
    Extend the basic twisted connection pool to provide a
    method that will use the psycopg dictfetchall() method.
    """

    def runDictQuery(self, *args, **kwargs):
        """
        Run a dictfetchall query. This is almost identical
        to the standard runQuery, except that it uses a
        custom method _runDictQuery()
        """
        return self.runInteraction(self._runDictQuery, *args, **kwargs)
                                   
    def _runDictQuery(self, trans, *args, **kwargs):
        """
        Run a dictfetchall() in the transaction.
        """
        trans.execute(*args, **kwargs)
        return trans.dictfetchall()

class SQLIterator(Iterator):
    """
    An SQLIterator allows you to connect to an RDBMS and run an SQL
    statement, the results of which are used as the iterator. This
    way, you can run a live query to the database when you want to
    iterate, rather than having to pre-run the query and dump to CSV.

    It supports any SQL connection engine supported by twisted.
    """

    def __init__(self, name, node):
        Iterator.__init__(self, name)
        
        # Set my necessary parameters
        DB_API = node.attrib['api']
        dbapi = __import__(DB_API)

        self.details = node.attrib['details']

        self.sql = node.find('sql').text
        log.debug("Will attempt to run SQL: %s" % self.sql)

        self.db = DictConnectionPool(DB_API, self.details, cp_noisy=False)

    def __iter__(self):
        """
        Get ready to iterate over the commands results
        """
        return self.iterlist.__iter__()
    
    def load_config(self, ignored):
        """
        Load configuration when required.
        """
        d = self.db.runDictQuery(self.sql)
        d.addCallback(self.got_result)

        return d

    def got_result(self, result):
        """
        Got result from the database.
        """
        self.iterlist = result
        log.debug("Got result from database: %s", result)

    def next(self):
        """
        Return the next item from the rows fetched from the database
        """
        log.debug("trying to return next item...")

def create_iterator(node):
    """
    Create an iterator from an element node
    """
    try:
        iter_name = node.attrib['name']
    except KeyError:
        raise ValueError("Iterator has no 'name' attribute defined")

    if node.attrib.has_key('type'):
        if node.attrib['type'].lower() == 'csv':
            log.info("Loading a CSV namespace...")
            iter = CSVIterator(iter_name, node)
            pass

        # SQL query support
        elif node.attrib['type'].lower() == 'sql':
            iter = SQLIterator(iter_name, node)
        
        else:
            raise ValueError("Unknown iterator dict type '%s'" % node.attrib['type'])
        
    # default to a plain iterator
    else:
        log.debug("setting up plain iterator...")
        iter = Iterator(iter_name)
        for elem in node.findall('dict'):
            ns = create_namespace(elem)
            iter.append(ns)
            pass

        log.debug("Added iterator '%s'", iter_name)
        pass
    return iter
