###############################################################################
# NAME: pyp_db.py
# VERSION: 2.0.0b3 (29NOVEMBER2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   createPedigreeDatabase()
#   createPedigreeTable()
#   loadPedigreeTable()
#   databaseQuery()
#   tableExists()
#   tableCountRows()
#   tableDropRows()
#   tableDropTable()
#   getCursor()
# AGGREGATES:
#   PypSum
#   PypMean
#   PypSVar
#   PypSSD
###############################################################################

##
# pyp_db contains a set of procedures for ...
##

import logging, math, os, string, sys
import pyp_io
import pyp_nrm
import pyp_utils

try:
    from pysqlite2 import dbapi2 as sqlite
except ImportError:
    # We could not import anything from pysqlite2.  D'oh!  It is either
    # not installed or it is installed in some strange place the the
    # PYTHONPATH needs update.
    logging.error('Unable to import pysqlite2 in pyp_db.py! \
        In order to use pyp_db you must install SQLite and pysqlite \
        for your platform.  For details see the file SQLITE.txt that is \
        distributed with PyPedal.')
    print '[ERRROR]: Unable to import pysqlite2 in pyp_db.py! \
        In order to use pyp_db you must install SQLite and pysqlite \
        for your platform.  For details see the file SQLITE.txt that is \
        distributed with PyPedal.'

##
# createPedigreeDatabase() creates a new database in SQLite.
# @param dbname The name of the database to create.
# @return A 1 on successful database creation, a 0 otherwise.
# @defreturn integer
def createPedigreeDatabase(dbname='pypedal'):
    # This is a sticky wicket.  This may be a completely unnecessary hack, but
    # it lets me create a new database without having to interact with the
    # command-line sqlite3 tool.
    _db_created = 0
    try:
        conn = sqlite.connect(dbname)
        curs = conn.cursor()
        HACK = "create table hack \
            ( \
                comment varchar(16) \
            );"
        curs.execute(HACK)
        curs.execute("INSERT INTO hack (comment) VALUES ('Hack create db.');")
        curs.close()
        conn.close()
        _db_created = 1
    except:
        logging.error('pyp_db/createPedigreeDatabase() was unable to successfully \
            create the pedigree database %s', dbname)
    return _db_created

##
# createPedigreeDatabase() creates a new pedigree table in a SQLite
# database.
# @param tablename The name of the table to create.
# @return A 1 on successful table creation, a 0 otherwise.
# @defreturn integer
def createPedigreeTable(curs,tablename='example'):
    _table_created = 0
    try:
        NEWTABLE = "create table %s \
            ( \
                animalID        integer UNIQUE, \
                animalName      varchar(128), \
                sireID          integer, \
                damID           integer, \
                generation      real, \
                infGeneration   real, \
                birthyear       integer, \
                sex             char(1), \
                coi             real, \
                founder         char(1), \
                ancestor        char(1), \
                originalID      text, \
                renumberedID    integer, \
                pedgreeComp     real, \
                breed           text, \
                age             real, \
                alive           char(1), \
                num_sons        integer, \
                num_daus        integer, \
                num_unk         integer, \
                herd            integer, \
                originalHerd    varchar(128), \
                gencoeff        real \
            );" % ( tablename )
        #print NEWTABLE
        curs.execute(NEWTABLE)
        _table_created = 1
    except:
        logging.error('pyp_db/createPedigreeTable() was unable to successfully \
            create the pedigree table %s', tablename)
    return _table_created

##
# loadPedigreeDatabase() takes a PyPedal pedigree object and loads
# the animal records in that pedigree into an SQLite table.
# @param pedobj A PyPedal pedigree object.
# @param dbname The database into which the pedigree will be loaded.
# @param tablename The table into which the pedigree will be loaded.
# @return A 1 on successful table load, a 0 otherwise.
# @defreturn integer
def loadPedigreeTable(pedobj):
    _table_loaded = 0
#     try:
    conn = sqlite.connect(pedobj.kw['database_name'])
    curs = conn.cursor()
    if not tableExists(pedobj.kw['database_name'],pedobj.kw['dbtable_name']):
        if pedobj.kw['messages'] == 'verbose':
            print "Table %s does not exist in database %s!" % ( pedobj.kw['dbtable_name'], pedobj.kw['database_name'] )
        logging.warning('Table %s does not exist in database %s!', pedobj.kw['dbtable_name'], pedobj.kw['database_name'])
        try:
            _tc = createPedigreeTable(curs,pedobj.kw['dbtable_name'])
            conn.commit()
            if _tc:
                if pedobj.kw['messages'] == 'verbose':
                    print "Table %s created in database %s." % ( pedobj.kw['dbtable_name'], pedobj.kw['database_name'] )
                logging.info('Table %s created in database %s!', pedobj.kw['dbtable_name'], pedobj.kw['database_name'])
            else:
                if pedobj.kw['messages'] == 'verbose':
                    print "Table %s could not be created in database %s." % ( pedobj.kw['dbtable_name'], pedobj.kw['database_name'] )
                logging.error('Table %s could not be created in database %s!', pedobj.kw['dbtable_name'], pedobj.kw['database_name'])
        except:
            return 0
    else:
        if pedobj.kw['messages'] == 'verbose':
            print "Table %s exists in database %s." % ( pedobj.kw['dbtable_name'], pedobj.kw['database_name'] )
        logging.info('Table %s exists in database %s!', pedobj.kw['dbtable_name'], pedobj.kw['database_name'])
        if tableCountRows(pedobj.kw['database_name'],pedobj.kw['dbtable_name']) > 0:
            if pedobj.kw['messages'] == 'verbose':
                print "Dropping %s rows from table %s." %  ( tableCountRows(pedobj.kw['database_name'],pedobj.kw['dbtable_name']), pedobj.kw['dbtable_name'] )
            logging.warning('Dropping %s rows from table %s!', tableCountRows(pedobj.kw['database_name'],pedobj.kw['dbtable_name']), pedobj.kw['dbtable_name'])
            tableDropRows(pedobj.kw['database_name'],pedobj.kw['dbtable_name'])

    for _p in pedobj.pedigree:
        MYROW = "INSERT INTO %s ( animalID, animalName, sireID, damID, generation, infGeneration, birthyear, sex, coi, founder, ancestor, originalID, renumberedID, pedgreeComp, breed, age, alive, num_sons, num_daus, num_unk, herd, originalHerd, gencoeff ) VALUES (%d, '%s', %d, %d, %f, %f, %d, '%s', %f, '%s', '%s', '%s', %d, %f, '%s', %d, '%s', %d, %d, %d, %d, '%s', %f)" % ( pedobj.kw['dbtable_name'], int(_p.animalID), _p.name, int(_p.sireID), int(_p.damID), float(_p.gen), float(_p.igen), int(_p.by), _p.sex, float(_p.fa), _p.founder, _p.ancestor, _p.originalID, int(_p.renumberedID), float(_p.pedcomp), _p.breed, int(_p.age), _p.alive, len(_p.sons), len(_p.daus), len(_p.unks), _p.herd, _p.originalHerd, _p.gencoeff )
        #print MYROW
        curs.execute(MYROW)
        myresult = curs.fetchall()

        ### What was I thinking?  The following code was executed for EACH row
        ### added to the table.  D'oh!

#             if myresult < 0:
#                 logging.error('pyp_db/createPedigreeTable() was unable to execute the SQL query %s', MYROW)
#             else:
#                 logging.info('pyp_db/createPedigreeTable() loaded the pedigree %s', pedobj.kw['pedname'])

    conn.commit()
    curs.close()
    conn.close()
    _table_loaded = 1
#     except:
#         logging.error('pyp_db/loadPedigreeTable() was unable to successfully load the pedigree %s', pedobj.kw['pedname'])
    return _table_loaded

##
# databaseQuery() executes an SQLite query.  This is a wrapper function
# used by the reporting functions that need to fetch data from SQLite.
# I wrote it so that any changes that need to be made in the way PyPedal
# talks to SQLite will only need to be changed in one place.
# @param sql A string containing an SQL query.
# @param _curs An [optional] SQLite cursor.
# @param dbname The database into which the pedigree will be loaded.
# @return The results of the query, or 0 if no resultset.
# @defreturn string
def databaseQuery(sql,curs=0,dbname='pypedal'):
    closeflag = 0
    try:
        if not curs:
            conn = sqlite.connect(dbname)
            curs = conn.cursor()
            closeflag = 1
        else:
            pass
        curs.execute(sql)
        myresult = curs.fetchall()
        if closeflag:
            curs.close()
            conn.close()
        else:
            pass
    except:
        myresult = 0
    return myresult

##
# tableExists() queries the sqlite_master view in an SQLite database to
# determine whether or not a table exists.
# @param dbname The database into which the pedigree will be loaded.
# @param tablename The table into which the pedigree will be loaded.
# @return A 1 if the table exists, a 0 otherwise.
# @defreturn integer
def tableExists(dbname='pypedal',tablename='example'):
    closeflag = 0
    _table_exists = 0
    try:
        teConn = sqlite.connect(dbname)
        teCurs = teConn.cursor()
        closeflag = 1
        MYTABLE = "select name from sqlite_master where type='table' and name='%s';" % (tablename)
        #print MYTABLE
        teCurs.execute(MYTABLE)
        myres = teCurs.fetchall()
        if len(myres) > 0:
            _table_exists = 1
        teCurs.close()
        teConn.close()
    except:
        logging.error('pyp_db/tableExists() was unable to query the pedigree database %s', dbname)
    return _table_exists

##
# tableCountRows() returns the number of rows in a table.
# @param dbname The database into which the pedigree will be loaded.
# @param tablename The table into which the pedigree will be loaded.
# @return The number of rows in the table 1 or 0.
# @defreturn integer
def tableCountRows(dbname='pypedal',tablename='example'):
    _table_rows = 0
    try:
        tcrConn = sqlite.connect(dbname)
        tcrCurs = tcrConn.cursor()
        MYQUERY = "select count(*) from %s;" % (tablename)
        tcrCurs.execute(MYQUERY)
        myres = tcrCurs.fetchone()
        if myres[0] > 0:
            _table_rows = myres[0]
        tcrCurs.close()
        tcrConn.close()
    except:
        logging.error('pyp_db/tableExists() was unable to query the pedigree database %s', dbname)
    #print _table_rows
    return _table_rows

##
# tableDropRows() drops all of the data from an existing table.
# @param dbname The database from which data will be dropped.
# @param tablename The table from which data will be dropped.
# @return A 1 if the data were dropped, a 0 otherwise.
# @defreturn integer
def tableDropRows(dbname='pypedal',tablename='example'):
    _table_dropped = 0
    try:
        dtcConn = sqlite.connect(dbname)
        dtcCurs = dtcConn.cursor()
        if tableExists(dbname,tablename):
            MYQUERY = "delete from %s where animalID <> '';" % (tablename)
            dtcCurs.execute(MYQUERY)
            dtcConn.commit()
            MYCOUNT = "select count(*) from %s;" % (tablename)
            dtcCurs.execute(MYCOUNT)
            myres = dtcCurs.fetchone()
            if myres[0] == 0:
                _table_dropped = 1
            logging.info('pyp_db/dropTableContents() dropped the contents of table %s in database %s', tablename, dbname)
        else:
            _table_dropped = 0
        dtcCurs.close()
        dtcConn.close()
    except:
        logging.error('pyp_db/dropTableContents() was unable to drop the contents of table %s in database %s', tablename, dbname)
    return _table_dropped

##
# tableDropTable() drops a table from the database.
# @param dbname The database from which the table will be dropped.
# @param tablename The table which will be dropped.
# @return 1
# @defreturn integer
def tableDropTable(dbname='pypedal',tablename='example'):
    dtcConn = sqlite.connect(dbname)
    dtcCurs = dtcConn.cursor()
    if tableExists(dbname,tablename):
        MYQUERY = "drop table %s;" % (tablename)
        #print MYQUERY
        dtcCurs.execute(MYQUERY)
        dtcConn.commit()
        logging.info('pyp_db/tableDropTable() dropped the table %s from database %s', tablename, dbname)
    dtcCurs.close()
    dtcConn.close()
    return 1

##
# getCursor() creates a database connection and returns a
# cursor on success or a 0 on failure.  It isvery useful for
# non-trivial queries because it creates SQLite aggrefates
# before returning the cursor.  The reporting routines in pyp_reports
# make heavy use of getCursor().
# @param dbname The database into which the pedigree will be loaded.
# @return An SQLite cursor if the database exists, a 0 otherwise.
# @defreturn cursor
def getCursor(dbname='pypedal'):
    try:
        gcConn = sqlite.connect(dbname)
        gcCurs = gcConn.cursor()
        gcConn.create_aggregate("pyp_sum", 1, PypSum)
        gcConn.create_aggregate("pyp_mean", 1, PypMean)
        gcConn.create_aggregate("pyp_svar", 1, PypSVar)
        gcConn.create_aggregate("pyp_ssd", 1, PypSSD)
        return gcCurs
    except:
        return 0

##
# PypSum is a user-defined aggregate for SQLite for returning sums from queries.
class PypSum:
     def __init__(self):
         self.count = 0

     def step(self, value):
         self.count += value

     def finalize(self):
         return self.count

##
# PypMean is a user-defined aggregate for SQLite for returning means from queries.
class PypMean:
     def __init__(self):
         self.count = 0.
         self.sum = 0.
         self.mean = 0.

     def step(self, value):
         self.count = self.count + 1
         self.sum = self.sum + value

     def finalize(self):
         self.mean = self.sum / self.count
         return self.mean

##
# PypSVar is a user-defined aggregate for SQLite for returning sample variances
# from queries.
class PypSVar:
     def __init__(self):
         self.count = 0.
         self.sum = 0.
         self.sumsq = 0.
         self.svar = 0.

     def step(self, value):
         self.count = self.count + 1
         self.sum = self.sum + value
         self.sumsq = self.sumsq + ( value ** 2 )

     def finalize(self):
         self.svar = ( self.sumsq - ( self.sum ** 2 / self.count ) ) / self.count - 1
         return self.svar

##
# PypSSD is a user-defined aggregate for SQLite for returning sample standard deviations
# from queries.
class PypSSD:
     def __init__(self):
         self.count = 0.
         self.sum = 0.
         self.sumsq = 0.
         self.svar = 0.
         self.ssd = 0.

     def step(self, value):
         self.count = self.count + 1
         self.sum = self.sum + value
         self.sumsq = self.sumsq + ( value ** 2 )

     def finalize(self):
         self.svar = ( self.sumsq - ( self.sum ** 2 / self.count ) ) / self.count - 1
         self.ssd = math.sqrt(self.svar)
         return self.ssd