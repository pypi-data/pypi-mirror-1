import sys
import logging
import os.path
import cPickle as pickle

from pymarc import MARCReader, MARCWriter
from bsddb3.db import DB, DB_BTREE, DB_CREATE

__version__ = '0.5'
_logger = logging.getLogger(__name__)


class Store():

    def __init__(self, dbfile='store.db'):
        db = DB()
        if os.path.exists(dbfile):
            _logger.debug("opening db %s" % dbfile)
            db.open(dbfile)
        else:
            _logger.debug("creating db %s" % dbfile)
            db.open(dbfile, dbtype=DB_BTREE, flags=DB_CREATE)
        self.db = db

    def load(self, filename, id_field='001', strict=False):
        """
        Load a batch of MARC21 data. By default the 001 field
        is used as a record identifier. But you can override
        this with the id_field parameter.
        """
        report = LoadReport()
        _logger.debug("loading %s" % filename)

        for record in MARCReader(file(filename)):
            try:
                record_type = record.leader[5]
                id = self._identifier(record, id_field=id_field)
                _logger.debug("got record type %s" % record_type)
                if record_type == 'c':
                    self.put(id, record)
                    report.updated += 1
                elif record_type == 'd':
                    self.delete(id)
                    report.deleted += 1
                elif record_type == 'n':
                    self.post(id, record)
                    report.created += 1

            except MissingIdentifier, e:
                report.missing_identifier += 1
                if strict:
                    raise e

            except NoRecordToUpdate, e:
                report.no_record_to_update += 1
                if strict:
                    raise e
                else: 
                    # when not in strict mode create a record
                    # when there is not one to update
                    id = self._identifier(record, id_field=id_field)
                    self.post(id, record)
                    report.created += 1

            except NoRecordToDelete, e:
                report.no_record_to_delete += 1
                if strict:
                    raise e

            finally:
                report.processed += 1

        return report

    def get(self, id):
        _logger.debug("fetching %s" % id)
        if self.db.has_key(id):
            return pickle.loads(self.db[id])
        return None

    def put(self, id, record):
        _logger.info("updating record: %s" % id)
        if self.db.has_key(id):
            self.db[id] = pickle.dumps(record)
        else:
            raise NoRecordToUpdate("missing record to update: %s" % id)

    def post(self, id, record):
        _logger.info("creating record: %s" % id)
        self.db[id] = pickle.dumps(record)

    def delete(self, id):
        _logger.info("deleting record: %s" % id)
        if self.db.has_key(id):
            self.db.delete(id)
        else:
            raise NoRecordToDelete("missing record to delete: %s" % id)

    def dump(self, filehandle=sys.stdout):
        writer = MARCWriter(filehandle)
        cursor = self.db.cursor()
        while True:
            entry = cursor.next()
            if entry == None:
                break
            _logger.debug("dumping %s" % entry[0])
            writer.write(pickle.loads(entry[1]))
        cursor.close()
        writer.close()

    def _identifier(self, record, id_field):
        if record[id_field] != None: 
            return record[id_field].data
        raise MissingIdentifier("missing identifier") 


class LoadReport:

    def __init__(self):
        self.processed = 0
        self.created = 0
        self.updated = 0
        self.deleted = 0
        self.missing_identifier = 0
        self.no_record_to_update = 0
        self.no_record_to_delete = 0

    def __str__(self):
        return \
"""

processed           %10i
created             %10i
updated             %10i
deleted             %10i
missing identifier  %10i
no record to update %10i
no record to delete %10i

""" % (self.processed, self.created, self.updated, self.deleted,
       self.missing_identifier, self.no_record_to_update,
       self.no_record_to_delete)

class LoadException(RuntimeError):
    pass

class MissingIdentifier(LoadException):
    pass

class NoRecordToUpdate(LoadException):
    pass

class NoRecordToDelete(LoadException):
    pass

