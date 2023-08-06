################################################################
# haufe.testrunner
#
# (C) 2007, Haufe Mediengruppe
################################################################

"""
Bootstrapping code
"""

import os
from optparse import OptionParser

from z3c.sqlalchemy import createSAWrapper, getSAWrapper
import sqlalchemy

from model import getModel
from config import WRAPPER_NAME


def createTables(option, opt_str, value, parser):
    """ create the media database """

    DB = getSAWrapper(WRAPPER_NAME)
    metadata = DB.metadata
    for name, d in DB.model.items():
        table = d['table'].tometadata(metadata)
        table.create(connectable=DB._engine)      



def createDatabase(option, opt_str, value, parser):
    """ low-level database creation """                

    DB = getSAWrapper(WRAPPER_NAME)

    cmd = 'dropdb --username %s --host %s %s' % (DB.username, DB.host, DB.dbname) 
    os.system(cmd)

    cmd = 'createdb -E UNICODE --username %s --host %s %s' % (DB.username, DB.host, DB.dbname)
    os.system(cmd)


def main():
    dsn = os.get('TESTING_DSN')
    if dsn is None:
        raise ValueError('$TESTING_DSN is undefined')

    wrapper = createSAWrapper(dsn, model=getModel, echo=False, name=WRAPPER_NAME)

    parser = OptionParser()
    parser.add_option('-d', '--create-db', action='callback', callback=createDatabase,
                      help='(Re)create database')
    parser.add_option('-t', '--create-tables', action='callback', callback=createTables,
                      help='Create tables')

    options, args = parser.parse_args()    


if __name__ == '__main__':
    main()
