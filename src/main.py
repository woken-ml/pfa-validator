#!/usr/bin/env python2.7

"""
This program validates a PFA file according the MIP (Medical Informatics Platform) output
specification.

It reads configurations from environment variables:
    INPUT_METHOD: FILE (default) or POSTGRESQL

    (if the FILE input method is chosen)
    PFA_PATH: the path to the PFA file

    (if the POSTRESQL input method is chosen)
    DB_HOST: host of the PostgreSQL server, without port
    DB_PORT: port where the postgresql server is listening
    DB_NAME: name of the DB that contains the PFA file
    DB_USER: username to connect to the PostgreSQL database
    DB_PASSWORD: password to connect to the PostgreSQL database
    DB_TABLE: Table that contains the PFA file
    DB_COLUMN: Column that contains the PFA file
    DB_WHERE_LVALUE: Left part of the SQL where close to perform, you should use the default value: 'job_id'
    DB_WHERE_RVALUE: Right part of the SQL where close to perform, you should use the JOB_ID and ignore this parameter
    JOB_ID: Job ID, this will override the DB_WHERE_RVALUE parameter

    (in order to validate that the model has existing variables names, we also need those)
    FEATURES_DB_HOST: host of the PostgreSQL server containing the data, without port
    FEATURES_DB_PORT: port where the postgresql server containing the data is listening
    FEATURES_DB_NAME: name of the DB that contains the data
    FEATURES_DB_USER: username to connect to the PostgreSQL database containing the data
    FEATURES_DB_PASSWORD: password to connect to the PostgreSQL database containing the data
"""

import sys
import os
from FileJSONPFAValidator import FileJSONPFAValidator
from PostgreSQLJSONPFAValidator import PostgreSQLJSONPFAValidator
from utils import print_error, print_ok


def main():
    # Instantiate a FileJSONPFAValidator or a PostgreSQLJSONPFAValidator depending which input method
    # is requested by the user
    input_method = os.getenv('INPUT_METHOD', 'FILE')

    validator = None

    if input_method == 'FILE':
        pfa_path = os.environ.get('PFA_PATH')
        validator = FileJSONPFAValidator(pfa_path)
        validator.load_document()

    elif input_method == 'POSTGRESQL':
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT')
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_table = os.environ.get('DB_TABLE')
        db_column = os.environ.get('DB_COLUMN')
        db_where_lvalue = os.environ.get('DB_WHERE_LVALUE')
        db_where_rvalue = os.environ.get('DB_WHERE_RVALUE')
        job_id = os.environ.get('JOB_ID')
        if job_id:
            db_where_rvalue = job_id
        validator = PostgreSQLJSONPFAValidator(db_host, db_port, db_name, db_user, db_password, db_table, db_column,
                                               db_where_lvalue, db_where_rvalue)
        validator.load_document()

    (valid, reason) = validator.validate()

    if not valid:
        print_error(reason)
        sys.exit(1)

    features_db_host = os.environ.get('FEATURES_DB_HOST')
    features_db_port = os.environ.get('FEATURES_DB_PORT')
    features_db_name = os.environ.get('FEATURES_DB_NAME')
    features_db_user = os.environ.get('FEATURES_DB_USER')
    features_db_password = os.environ.get('FEATURES_DB_PASSWORD')
    features_db_table = os.environ.get('FEATURES_DB_TABLE')

    # Validate that the model has existing variables names
    (valid, reason) = validator.validate_io(features_db_host, features_db_port, features_db_name, features_db_user,
                                            features_db_password, features_db_table)

    if not valid:
        print_error(reason)
        sys.exit(1)

    print_ok("This is a valid PFA document!")


if __name__ == '__main__':
    main()
