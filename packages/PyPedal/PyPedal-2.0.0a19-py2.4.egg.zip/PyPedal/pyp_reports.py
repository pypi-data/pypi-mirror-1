###############################################################################
# NAME: pyp_reports.py
# VERSION: 2.0.0a19 (22JULY2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   meanMetricBy()
###############################################################################

##
# pyp_reports contains a set of procedures for ...
##

import logging, os, string, sys
import pyp_io, pyp_nrm, pyp_utils

global metric_to_column
global byvar_to_column

metric_to_column = {'fa':'coi'}
byvar_to_column = {'by':'birthyear',
                  'gen':'generation'}

try:
    from pysqlite2 import dbapi2 as sqlite
except ImportError:
    # We could not import anything from pysqlite2.  D'oh!  It is either
    # not installed or it is installed in some strange place the the
    # PYTHONPATH needs update.
    logging.error('Unable to import pysqlite2 in pyp_reports.py! \
        In order to use pyp_reports you must install SQLite and pysqlite \
        for your platform.  For details see the file SQLITE.txt that is \
        distributed with PyPedal.')
    print '[ERRROR]: Unable to import pysqlite2 in pyp_reports.py! \
        In order to use pyp_reports you must install SQLite and pysqlite \
        for your platform.  For details see the file SQLITE.txt that is \
        distributed with PyPedal.'

##
# meanMetricBy() ...
# @param pedobj A PyPedal pedigree object.
# @param metric The variable to summarize on a BY variable.
# @param byvar The variable on which to group the metric.
# @return A dictionary containing means for the metric variable keyed to levels of the byvar.
# @defreturn dictionary
def meanMetricBy(pedobj,metric='fa',byvar='by'):
    try:
        import pyp_db
    except ImportError:
        logging.error('Unable to import pyp_db.py in pyp_reports/animalMetricBy().')
        return 0

    try:
        if metric not in ['fa']:
            logging.warning('You passed an unrecognized variable, %s, to pyp_reports/animalMetricBy() in the METRIC field.  It has been changed to \'fa\' (coefficient of inbreeding).',metric)
            metric = 'fa'
        if byvar not in ['gen','sex','birthyear','by']:
            logging.warning('You passed an unrecognized variable, %s, to pyp_reports/animalMetricBy() in the BYVAR field.  It has been changed to \'by\' (birth year).',byvar)
            byvar = 'by'

        curs = pyp_db.getCursor(pedobj.kw['database_name'])
        MYQUERY = "SELECT %s,pyp_mean(%s) FROM %s GROUP BY %s ORDER BY %s ASC" % \
            (byvar_to_column[byvar], metric_to_column[metric],pedobj.kw['dbtable_name'], \
            byvar_to_column[byvar], byvar_to_column[byvar])
        curs.execute(MYQUERY)
        myresult = curs.fetchall()
        result_dict = {}
        for _mr in myresult:
            _level, _mean = _mr
            result_dict[_level] = _mean
        logging.info('pyp_reports/meanMetricBy() report completed.')
        return result_dict
    except:
        return 0