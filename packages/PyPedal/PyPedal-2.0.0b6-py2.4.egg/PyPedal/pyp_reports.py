###############################################################################
# NAME: pyp_reports.py
# VERSION: 2.0.0b3 (28NOVEMBER2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   meanMetricBy()
#   pdfMeanMetricBy()
#   pdfPedigreeMetadata()
#   _pdfInitialize()
#   _pdfDrawPageFrame()
#   _pdfCreateTitlePage()
###############################################################################

##
# pyp_reports contains a set of procedures for ...
##

import logging, os, string, sys
import pyp_io
import pyp_nrm
import pyp_utils

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas

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
# meanMetricBy() returns a dictionary of means keyed by levels of the 'byvar' that
# can be used to draw graphs or prepare reports of summary statistics.
# @param pedobj A PyPedal pedigree object.
# @param metric The variable to summarize on a BY variable.
# @param byvar The variable on which to group the metric.
# @param createpdf Flag indicating whether or not a PDF version of the report should be created.
# @return A dictionary containing means for the metric variable keyed to levels of the byvar.
# @defreturn dictionary
def meanMetricBy(pedobj,metric='fa',byvar='by', createpdf=0):
    try:
        import pyp_db
    except ImportError:
        logging.error('Unable to import pyp_db.py in pyp_reports/animalMetricBy().')
        return 0

    try:
        if metric not in ['fa']:
            logging.warning('You passed an unrecognized variable, %s, to pyp_reports/animalMetricBy() in the METRIC field.  It has been changed to \'fa\' (coefficient of inbreeding).', metric)
            metric = 'fa'
        if byvar not in ['gen','sex','birthyear','by']:
            logging.warning('You passed an unrecognized variable, %s, to pyp_reports/animalMetricBy() in the BYVAR field.  It has been changed to \'by\' (birth year).', byvar)
            byvar = 'by'

        curs = pyp_db.getCursor(pedobj.kw['database_name'])

        # We need to check and see if the pedigree has already been loaded into the
        # database.  If it has not, go ahead and do that in the background.
        if not pyp_db.tableExists(pedobj.kw['database_name'], pedobj.kw['dbtable_name']):
            pyp_db.loadPedigreeTable(pedobj)
            logging.warning('The pedigree %s has not been loaded into the database.  Loading now.', pedobj.kw['database_name'])
            if pedobj.kw['messages'] == 'verbose':
                print 'The pedigree %s has not been loaded into the database.  Loading now.' % \
                    ( pedobj.kw['database_name'] )

        # Once we know that the pedigree has been loaded into the database we can create the report.
        MYQUERY = "SELECT %s,pyp_mean(%s) FROM %s GROUP BY %s ORDER BY %s ASC" % \
            (byvar_to_column[byvar], metric_to_column[metric],pedobj.kw['dbtable_name'], \
            byvar_to_column[byvar], byvar_to_column[byvar])
        #print MYQUERY
        curs.execute(MYQUERY)
        myresult = curs.fetchall()
        result_dict = {}
        for _mr in myresult:
            _level, _mean = _mr
            result_dict[_level] = _mean
        logging.info('pyp_reports/meanMetricBy() report completed.')

        if createpdf:
            try:
                mmbPdfTitle = '%s_mean_metric_%s_%s' % \
                    (pedobj.kw['default_report'], metric, byvar)
                _mmbPdf = pdfMeanMetricBy(pedobj, result_dict, 1, mmbPdfTitle)
                if _mmbPdf:
                    logging.info('pyp_reports/pdfMeanMetricBy() succeeded.')
                else:
                    logging.error('pyp_reports/pdfMeanMetricBy() failed.')
            except:
                pass

        return result_dict
    except:
        return 0

##
# pdfMeanMetricBy() returns a dictionary of means keyed by levels of the 'byvar' that
# can be used to draw graphs or prepare reports of summary statistics.
# @param pedobj A PyPedal pedigree object.
# @param results A dictionary containing means for the metric variable keyed to levels of the byvar.
# @param titlepage Show (1) or hide (0) the title page.
# @param reporttitle Title of report; if '', _pdfTitle is used.
# @param reportauthor Author/preparer of report.
# @param reportfile Optional name of file to which the report should be written.
# @return 1 on success, 0 on failure
# @defreturn integer
def pdfMeanMetricBy(pedobj, results, titlepage=0, reporttitle='', reportauthor='', reportfile=''):
    try:
        import reportlab
    except ImportError:
        logging.error('Unable to import ReportLab in pyp_reports/pdfMeanMetricBy().')
        return 0

    try:
        if reportfile == '':
            _pdfOutfile = '%s_mean_metric_by.pdf' % ( pedobj.kw['default_report'] )
        else:
            _pdfOutfile = reportfile
        if pedobj.kw['messages'] == 'verbose':
            print 'Writing meanMetricBy report to %s' % ( _pdfOutfile )
        logging.info('Writing meanMetricBy report to %s', _pdfOutfile )

        _pdfSettings = _pdfInitialize(pedobj)
        canv = canvas.Canvas(_pdfOutfile, invariant=1)
        canv.setPageCompression(1)

        if titlepage:
            if reporttitle == '':
                reporttitle = 'meanMetricBy Report for Pedigree\n%s' % (pedobj.kw['pedname'])
            _pdfCreateTitlePage(canv, _pdfSettings, reporttitle, reportauthor)
        _pdfDrawPageFrame(canv, _pdfSettings)

        canv.setFont("Times-Bold", 12)
        tx = canv.beginText( _pdfSettings['_pdfCalcs']['_left_margin'],
            _pdfSettings['_pdfCalcs']['_top_margin'] - 0.5 * _pdfSettings['_pdfCalcs']['_unit'] )
        # This is where the actual content is written to a text object that will be displayed on
        # a canvas.
        for _k, _v in results.iteritems():
            if len(str(_k)) <= 14:
                _line = '\t%s:\t\t%s' % (_k, _v)
            else:
                _line = '\t%s:\t%s' % (_k, _v)
            tx.textLine(_line)
            if tx.getY() < _pdfSettings['_pdfCalcs']['_bottom_margin'] + \
                0.5 * _pdfSettings['_pdfCalcs']['_unit']:
                canv.drawText(tx)
                canv.showPage()
                _pdfDrawPageFrame(canv, _pdfSettings)
                canv.setFont('Times-Roman', 12)
                tx = canv.beginText( _pdfSettings['_pdfCalcs']['_left_margin'],
                    _pdfSettings['_pdfCalcs']['_top_margin'] -
                    0.5 * _pdfSettings['_pdfCalcs']['_unit'] )
        if tx:
            canv.drawText(tx)
            canv.showPage()
        canv.save()
        return 1
    except:
        return 0

##
# pdfPedigreeMetadata() produces a report, in PDF format, of the metadata from
# the input pedigree.  It is intended for use as a template for custom printed
# reports.
# @param pedobj A PyPedal pedigree object.
# @param titlepage Show (1) or hide (0) the title page.
# @param reporttitle Title of report; if '', _pdfTitle is used.
# @param reportauthor Author/preparer of report.
# @param reportfile Optional name of file to which the report should be written.
# @return A 1 on success, 0 otherwise.
# @defreturn integer
def pdfPedigreeMetadata(pedobj, titlepage=0, reporttitle='', reportauthor='', reportfile=''):
    try:
        import reportlab
    except ImportError:
        logging.error('Unable to import ReportLab in pyp_reports/pdfPedigreeMetadata().')
        return 0

    if reportfile == '':
        _pdfOutfile = '%s_metadata.pdf' % ( pedobj.kw['default_report'] )
    else:
        _pdfOutfile = reportfile
    if pedobj.kw['messages'] == 'verbose':
        print 'Writing metadata report to %s' % ( _pdfOutfile )
    logging.info('Writing metadata report to %s', _pdfOutfile )

    # The _pdfSettings dictionary contains several settings, such as page size,
    # page height and width, and margins, that are used several times.
    _pdfSettings = _pdfInitialize(pedobj)

    # The actual report is written to an instance of a canvas object, which is
    # stored in a file whose name is _pdfOutfile.  We have to create this canvas
    # before we can start assembling our report.
    canv = canvas.Canvas(_pdfOutfile, invariant=1)
    canv.setPageCompression(1)

    # Add a title page to the report if the user wants one.
    if titlepage:
        if reporttitle == '':
            reporttitle = 'Metadata for Pedigree\n%s' % (pedobj.kw['pedname'])
        _pdfCreateTitlePage(canv, _pdfSettings, reporttitle, reportauthor)

    # Start a new page of output.  Split the metadata output returned by the
    # stringme() method on linebreak characters and write each of the resulting
    # tokens to the canvas.
    _pdfDrawPageFrame(canv, _pdfSettings)
    canv.setFont("Times-Bold", 12)
    tx = canv.beginText( _pdfSettings['_pdfCalcs']['_left_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'] - 0.5 * _pdfSettings['_pdfCalcs']['_unit'] )
    _metadata_string = string.split(pedobj.metadata.stringme(), '\n')
    for _m in _metadata_string:
        tx.textLine(_m)
        # Page breaking has to be done manually.  Oh, well, I was able to steal, er,
        # borrow this but from odyssey.py.
        if tx.getY() < _pdfSettings['_pdfCalcs']['_bottom_margin'] + \
            0.5 * _pdfSettings['_pdfCalcs']['_unit']:
            canv.drawText(tx)
            canv.showPage()
            _pdfDrawPageFrame(canv, _pdfSettings)
            canv.setFont('Times-Roman', 12)
            tx = canv.beginText( _pdfSettings['_pdfCalcs']['_left_margin'],
                _pdfSettings['_pdfCalcs']['_top_margin'] -
                0.5 * _pdfSettings['_pdfCalcs']['_unit'] )

            pg = canv.getPageNumber()
            if pedobj.kw['messages'] == 'verbose' and pg % 10 == 0:
                print 'Printed page %d' % pg

    # Finish the document.  You need to draw the text object to the canvas and
    # call the showPage() method on the canvas so that your changes are visible.
    if tx:
        canv.drawText(tx)
        canv.showPage()
        # The following line inserts a blank page.  It was in the odyssey.py
        # example distributed with ReportLab, but I'm not sure why.  If the
        # last page of your document is getting chopped off try uncommenting
        # this line.
        #_pdfDrawPageFrame(canv, _pdfSettings)

    # Once your report has been assembled it must be written to disc.  If you
    # omit the 'canv.save()' line then your PDF will never be written to a file.
    canv.save()

###############################################################################
# _pdfDrawPageFrame() was taken from the procedure drawPageFrame() included in
# the demo program odyssey.py in the ReportLab distribution.  _pdfInitialize()
# is rolled together using some of the code in odyssey.py as an example, as
# well as some of my own work.
###############################################################################

##
# _pdfInitialize() returns a dictionary of metadata that is used for report
# generation.
# @param pedobj A PyPedal pedigree object.
# @return A dictionary of metadata that is used for report generation.
# @defreturn dictionary
def _pdfInitialize(pedobj):
    _pdfSettings = {}
    _pdfSettings['_pdfTitle'] = pedobj.kw['pedname']
    _pdfSettings['_pdfPageinfo'] = pedobj.kw['filetag']
    # Calculate margins, etc.
    _pdfCalcs = {}
    if pedobj.kw['default_unit'] == 'inch':
        _pdfCalcs['_unit'] = inch
    else:
        _pdfCalcs['_unit'] = cm
    if pedobj.kw['paper_size'] == 'letter':
        _pdfCalcs['_page'] = letter
        _pdfCalcs['_top_margin'] = letter[1] - inch
        _pdfCalcs['_bottom_margin'] = inch
        _pdfCalcs['_left_margin'] = inch
        _pdfCalcs['_right_margin'] = letter[0] - inch
        _pdfCalcs['_frame_width'] = _pdfCalcs['_right_margin'] - _pdfCalcs['_left_margin']
        _pdfCalcs['_page_width'] = letter[0]
        _pdfCalcs['_page_height'] = letter[1]
    else:
        _pdfCalcs['_page'] = A4
        _pdfCalcs['_top_margin'] = A4[1] - inch
        _pdfCalcs['_bottom_margin'] = inch
        _pdfCalcs['_left_margin'] = inch
        _pdfCalcs['_right_margin'] = A4[0] - inch
        _pdfCalcs['_frame_width'] = _pdfCalcs['_right_margin'] - _pdfCalcs['_left_margin']
        _pdfCalcs['_page_width'] = A4[0]
        _pdfCalcs['_page_height'] = A4[1]
    _pdfSettings['_pdfCalcs'] = _pdfCalcs
    return _pdfSettings

##
# _pdfDrawPageFrame() nicely frames page contents and includes the
# document title in a header and the page number in a footer.
# @param canv An instance of a ReportLab Canvas object.
# @param _pdfSettings An options dictionary created by _pdfInitialize().
# @return None
# @defreturn None
def _pdfDrawPageFrame(canv, _pdfSettings):
    # Write the report title in the top, left-hand corner of the page.
    canv.line(_pdfSettings['_pdfCalcs']['_left_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'],
        _pdfSettings['_pdfCalcs']['_right_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'])
    canv.setFont('Times-Italic', 12)
    canv.drawString(_pdfSettings['_pdfCalcs']['_left_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'] + 2,
        _pdfSettings['_pdfTitle'])

    # Write the date/time in the top, right-hand corner of the page.
    canv.line(_pdfSettings['_pdfCalcs']['_left_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'],
        _pdfSettings['_pdfCalcs']['_right_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'])
    canv.setFont('Times-Italic', 12)
    canv.drawString(_pdfSettings['_pdfCalcs']['_right_margin'] - \
        1.85 * _pdfSettings['_pdfCalcs']['_unit'],
        _pdfSettings['_pdfCalcs']['_top_margin'],
        pyp_utils.pyp_nice_time())

    # Write the page number bottom center.
    canv.line(_pdfSettings['_pdfCalcs']['_left_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'],
        _pdfSettings['_pdfCalcs']['_right_margin'],
        _pdfSettings['_pdfCalcs']['_top_margin'])
    canv.line(_pdfSettings['_pdfCalcs']['_left_margin'],
        _pdfSettings['_pdfCalcs']['_bottom_margin'],
        _pdfSettings['_pdfCalcs']['_right_margin'],
        _pdfSettings['_pdfCalcs']['_bottom_margin'])
    canv.drawCentredString(0.5 * _pdfSettings['_pdfCalcs']['_page'][0],
        0.5 * _pdfSettings['_pdfCalcs']['_unit'],
        "Page %d" % canv.getPageNumber())

##
# _pdfCreateTitlePage() adds a title page to a ReportLab canvas object.
# @param canv An instance of a ReportLab Canvas object.
# @param _pdfSettings An options dictionary created by _pdfInitialize().
# @return None
# @defreturn None
def _pdfCreateTitlePage(canv, _pdfSettings, reporttitle = '', reportauthor = ''):
    import textwrap
    _pdfDrawPageFrame(canv, _pdfSettings)
    # _title_y is the y-coordinate at which a given line of the title should be
    # printed.  It is defined here because both the title and the author renderers
    # need to see it.
    _title_y = 7 * _pdfSettings['_pdfCalcs']['_unit']
    canv.setFont("Times-Bold", 36)
    if reporttitle == '':
        canv.drawCentredString(0.5 * _pdfSettings['_pdfCalcs']['_page'][0],
            7 * _pdfSettings['_pdfCalcs']['_unit'], _pdfSettings['_pdfTitle'])
    else:
        # This is potentially confusing, so here goes: we're going to split
        # the title on '\n's and write each resulting bit of text on its own
        # line.  drawCentredString() does not automatically do this so I had
        # to hack it on.
        _bits = string.split(reporttitle, '\n')
        for _b in _bits:
            # Based strictly on observation we need to wrap titles longer than 26
            # characters when using the default 36-point typeface.
            if len(_b) > 26:
                _b_wrapped = textwrap.wrap(_b, 26, break_long_words=True)
#                 print _b_wrapped
                for _bw in _b_wrapped:
                    canv.drawCentredString( 0.5 * _pdfSettings['_pdfCalcs']['_page'][0], \
                        _title_y, _bw)
                    _title_y = _title_y - 1 * _pdfSettings['_pdfCalcs']['_unit']
            else:
                canv.drawCentredString( 0.5 * _pdfSettings['_pdfCalcs']['_page'][0], _title_y, _b)
                _title_y = _title_y - 1 * _pdfSettings['_pdfCalcs']['_unit']
    # Only print the author's name if there is one.  A report is not required to have an
    # author.
    if reportauthor != '':
        canv.setFont("Times-Bold", 18)
        canv.drawCentredString(0.5 * _pdfSettings['_pdfCalcs']['_page'][0],
            _title_y, reportauthor)
    canv.showPage()