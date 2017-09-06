"""
Module used for rethinkdb related functionality.
"""
import logging
import rethinkdb as r
from datetime import datetime

class RethinkDB:
    """
    Class which represents rethinkdb database.
    """
    def __init__(self, host, port, database):
        """
        Method used to initialize this tool.
        :param host: host to where the database is located at.
        :param port: port where the database is located at.
        :return: nothing.
        """
        self.host = host
        self.port = port
        self.database = database

        try:
            self.connection = r.connect(host, port)
        except r.ReqlDriverError:
            logging.debug("Could not connect to database...")
            exit(1)

    def add_experiment(self, table_experiments):
        """
        Method to add new experiment information.
        :param table_experiments: the table that is used to store experiment related documents.
        :return: the experiment document id.
        """
        return self.add_document(table_experiments, {'createdAt': get_date_now()})

    def add_analytics(self, table_analytics, experiment_id, analytics):
        """
        Method to add new analytics information.
        :param table_analytics: the table that is used to store analytics related documents.
        :param experiment_id: the experiment id to which this transformation belongs.
        :param analytics: the analytics itself (dict() object) that should be added as a document.
        :return: the experiment document id.
        """
        return self.add_document(table_analytics, {'createdAt': get_date_now(),
                                                   'experiment_id': experiment_id,
                                                   'analytics': analytics})

    def add_transformation(self, table_transformations, experiment_id, version_name, transformation):
        """
        Method used to add new transformation information.
        :param table_transformations: the table that is used to store transformation related documents.
        :param experiment_id: the experiment id to which this transformation belongs.
        :param version_name: the name of this specific transformation version.
        :param transformation: the transformation itself (dict() object) that should be added as a document.
        :return: the transformation document id.
        """
        return self.add_document(table_transformations,
                                 {'createdAt': get_date_now(),
                                  'experiment_id': experiment_id,
                                  'version_name': version_name,
                                  'transformation': transformation})

    def add_test(self, table_tests, experiment_id, version, test):
        """
        Method used to add new test information.
        :param table_tests: the table that is used to store test related documents.
        :param experiment_id: the experiment id to which this test belongs.
        :param base_version: the test base executable version.
        :param mobile_version: the test mobile blocks version.
        :param test: the test information itself (dict() object) that should be added as a document.
        :return: the test document id.
        """
        return self.add_document(table_tests,
                                 {'createdAt': get_date_now(),
                                  'experiment_id': experiment_id,
                                  'version': version,
                                  'test_data': test})

    def add_document(self, table, document):
        """
        Method used to add a document to a given table.
        :param table: the table to which the document should be added.
        :param document: the document (dict() object) that should be added.
        :return: the id of the document.
        """
        result = r.db(self.database).table(table).insert(document).run(self.connection)
        generated_id = result['generated_keys'][0]
        logging.debug('RethinkDB: created new document with id: ' + generated_id)
        return generated_id


def get_date_now():
    """
    Method used to get the current datetime.
    :return: the current datetime.
    """
    return datetime.now(r.make_timezone('02:00'))