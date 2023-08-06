# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.

import os
import mimetypes
import smtplib
import sys
import time

from argparse import ArgumentParser
from datetime import datetime,timedelta
from email import Encoders
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from cStringIO import StringIO
from glob import glob

def parse_log(paths,td_from,td_to,out,LogRow,processors,summary,live_output):

    unprocessable = []
    earliest = None
    latest = None
    lines_total = 0
    hits_total = 0.0
    skipped_total = 0
    errors_total = 0

    process_start = time.time()
    for path in paths:
        if live_output:
            print 'Processing',path
        for line in open(path):
            lines_total += 1
            if live_output and not lines_total%100:
                print '\r%i processed, %i skipped, %i errored' % (
                    lines_total,
                    skipped_total,
                    errors_total,
                    ),
            row = LogRow(line,path)
            if not row.valid:
                errors_total += 1
                unprocessable.append(line)
            else:
                # timestamping
                if td_from and row.timestamp < td_from:
                    skipped_total +=1
                    continue
                if td_to and row.timestamp > td_to:
                    skipped_total +=1
                    continue
                if latest is None or row.timestamp > latest:
                    latest=row.timestamp
                if earliest is None or row.timestamp < earliest:
                    earliest=row.timestamp
                hits_total += 1
                for processor in processors:
                    processor.process(row)
        if live_output:
            print 
    process_end = time.time()
    print >>out

    if latest and earliest:        
        hits_period = latest-earliest
        hps = float(hits_total)/float(hits_period.days*24*60*60+hits_period.seconds+(float(hits_period.microseconds)/1000000.0))
    else:
        hits_period = '0s'
        hps = 0
    lines_period = process_end-process_start
    lps = float(lines_total)/float(lines_period)
    ### summarisation here
    if td_from and td_to:
        include_period = 'between %s and %s' % (td_from,td_to)
    elif td_from:
        include_period = 'after %s' % td_from
    elif td_to:
        include_period = 'before %s' % td_to
    else:
        include_period = 'in processed log files.'
    print >>out, 'Processing entries that occurred '+include_period
    print >>out, '%d lines analysed (including %d skipped, %d errored) in %.0f seconds at %.2f lines/sec' % (
        lines_total,
        skipped_total,
        errors_total,
        lines_period,
        lps
        )
    print >>out
    print >>out, 'earliest entry processed:',earliest
    print >>out, '  latest entry processed:',latest
    print >>out
    print >>out, '%i hits in %s at an average of %.2f hits/sec' % (hits_total,hits_period,hps)
    print >>out
    filepaths = summary(out,hits_total,hps)
    ### end of summarisation
    errors_to_show = 10
    if errors_total:
        shown_errors = min(errors_total,errors_to_show)
        print >>out
        print >>out, errors_total,'line(s) could not be analysed, first %i:' % shown_errors
        print >>out
        for line in unprocessable[:errors_to_show]:
            print >>out, repr(line)
    return filepaths

def main(LogRow,processors,summary,argv=None):
    parser = ArgumentParser()

    parser.add_argument("path", nargs='+',
                        help="The log file(s) to analyze. Can include globbing characters."
                             " and can be specified multiple times.")
    
    parser.add_argument("-F", "--from", dest="td_from",metavar="YYYY/MM/DD-HH:MM:SS",
                        help="Specify the date/time of earliest log entry to analyse."
                             "Defaults to 00:00:00 of the date prior to the current date.")

    parser.add_argument("-T", "--to", dest="td_to",metavar="YYYY/MM/DD-HH:MM:SS",
                        help="Specify the date/time prior to which all log entry will be analysed."
                        "Defaults to 00:00:00 of the current date.")

    parser.add_argument("-A", "--all", dest="td_all",action="store_true",
                        help="Specify that all entries in the log file should be proccessed")

    parser.add_argument("-O", "--originator", dest="originator",
                        help="Specify the From address for any mail sent."
                             "Defaults to the first email address supplied in -E")
    
    parser.add_argument("-E", "--email", action="append",
                        help="Specify the To address for mail notification.")
    
    parser.add_argument("-S", "--subject", dest="subject",
                        help="Specify a subject for any emails sent")
    
    parser.add_argument("-V", "--verbose", dest="verbose",action="store_true",
                        help="Force the display of progress information.")

    options = parser.parse_args(argv)
    
    options.paths = []    
    for path in options.path:
        options.paths.extend(glob(path))
    if not options.paths:
        parser.error('None of %s match any log files' % (', '.join(options.path)))

    for path in options.paths:
        if not os.path.exists(path):
            parser.error('%s does not exist!'%path)

    if options.td_all and (options.td_from or options.td_to):
        parser.error('-A cannot be used in conjunction with -F or -T')

    if options.td_all:
        td_from = None
        td_to = None
    else:
        today_start = datetime(*time.localtime()[0:3])
        if options.td_from:
            td_from = datetime(*time.strptime(options.td_from,'%Y/%m/%d-%H:%M:%S')[0:6])
        else:
            if options.td_to:
                td_from = None
            else:
                td_from = today_start-timedelta(days=1)
        if options.td_to:
            td_to = datetime(*time.strptime(options.td_to,'%Y/%m/%d-%H:%M:%S')[0:6])
        else:
            if options.td_from:
                td_to = None
            else:
                td_to = today_start

    if options.email:
        out = StringIO()
    else:
        out = sys.stdout
        
    parse_log(options.paths,td_from,td_to,out,LogRow,processors,summary,options.verbose)
    
    if options.email:
        if not options.subject:
            options.subject = 'Log Analysis Results'
        if not options.originator:
            options.originator = options.email[0]
        
        msg = MIMEText(out.getvalue())

        msg['Subject'] = options.subject
        msg['From'] = options.originator
        msg['To'] = ', '.join(options.email)
        
        s = smtplib.SMTP()
        s.connect()
        s.sendmail(options.originator, options.email, msg.as_string())
        s.close()

