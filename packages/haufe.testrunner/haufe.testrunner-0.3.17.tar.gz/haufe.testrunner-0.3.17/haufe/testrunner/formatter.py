##########################################################################
# haufe.testrunner
#
# (C) 2007, Haufe Mediengruppe
##########################################################################


import os
import socket
import pwd
from datetime import datetime

from styles import styles

now = datetime.now()
now_str = now.strftime('%d.%m.%Y %H:%M:%S')
hostname = socket.gethostname()
ipaddr = socket.gethostbyname(hostname)


def text(results, options, testrunner_id=None, run_id=None):
    """ Write results dict to a text file. 
        Returns the generated report as string.
    """

    fn = os.path.join(options.log_dir, 'report.txt')
    fp = open(fn, 'w')

    print >>fp, 'Testrunner results (%s)' % options.ident
    print >>fp, 'Generated: %s (%s/%s)' % (now_str, hostname, ipaddr)
    print >>fp 
    print >>fp, 'Module                           Status  Tests OK'
    print >>fp, '-------------------------------------------------'

    for k in sorted(results.keys()):

        ok_str = results[k]['tests_ok'] and 'OK' or 'FAILED'
        num_tests = results[k]['number_tests']
        num_failures = results[k]['number_failures']
        num_str = '%s/%s' % (num_tests-num_failures , num_tests)

        print >>fp, '%-30s   %-6s   %s' % (k, ok_str, num_str)
        if not results[k]['tests_ok']:
           print >>fp, '    %s/%s' % (options.base_url, results[k]['logfile']) 

    if testrunner_id and run_id:
        print >>fp
        print >>fp, 'Details: %s/showresults?testrunner_id:int=%d&run_id:int=%d' % (options.base_url, testrunner_id, run_id)
        print >>fp, 'RSS Feed: %s/rss?testrunner_id:int=%d' % (options.base_url, testrunner_id)
    fp.close()

    return open(fn).read()


def html (results, options):
    """ Write results dict to a HTML file. 
        Returns the generated report as string.
    """

    fn = os.path.join(options.log_dir, 'index.html')
    fp = open(fn, 'w')

    print >>fp, '<html><body>'
    print >>fp, '<head>'

    if options.stylesheet:
        print >>fp, '    <link type="text/css" rel="stylesheet" src="%s">' % options.stylesheet
    else:
        print >>fp, '    <style type="text/css" >'
        print >>fp, styles
        print >>fp, '    </style>'

    print >>fp, '</head>'
    print >>fp, '<body>'
    print >>fp, '<h1>Testrunner results (%s)</h1>' % options.ident
    print >>fp, '<h3>Generated: %s (%s/%s)</h3>' % (now_str, hostname, ipaddr)

    print >>fp, '<table border="1">' 
    print >>fp, '  <thead>' 
    print >>fp, '    <tr>' 
    print >>fp, '      <th>Module</th>' 
    print >>fp, '      <th>Status</th>' 
    print >>fp, '      <th>Tests OK</th>' 
    print >>fp, '      <th>Link</th>' 
    print >>fp, '    </tr>' 
    print >>fp, '  </thead>' 

    print >>fp, '  <tbody>' 

    for k in sorted(results.keys()):

        ok_str = results[k]['tests_ok'] and 'OK' or 'FAILED'
        num_tests = results[k]['number_tests']
        num_failures = results[k]['number_failures']
        num_str = '%s/%s' % (num_tests-num_failures , num_tests)
        url = '%s/%s' % (options.base_url, results[k]['logfile']) 

        print >>fp, '    <tr class="%s">' % ok_str.upper() 
        print >>fp, '      <td class="MODULE">%s</td>' % k
        print >>fp, '      <td class="%s">%s</td>' % (ok_str.upper(), ok_str)
        print >>fp, '      <td class="COUNTED">%s</td>' % num_str
        print >>fp, '      <td class="LINK"><a href="%s">Log</a></td>' % url 
        print >>fp, '    </tr>' 

    print >>fp, '  </tbody>' 
    print >>fp, '</table>' 

    print >>fp, '<hr/>'
    print >>fp, '<div class="FEED">Feed:'
    rss_url = '%s/logs/index.rss' % options.base_url
    print >>fp, '<a href="%s">%s</a>' % (rss_url, rss_url)
    print >>fp, '</div>'
    print >>fp, '</body></html>' 
    print >>fp
    
    fp.close()

    return open(fn).read()


def collect_rss(options):

    dirnames = []

    for dirname in os.listdir(options.log_root):
        if not os.path.isdir(os.path.join(options.log_root, dirname)):
            continue

        dirnames.append(dirname)

    dirnames.sort()
    dirnames.reverse()
    return dirnames[:50]


def rss(results, options, tests_failed):
    """ Generate or update RSS file """

    if tests_failed:
        subject = '%s - FAILED (%s)' % (options.ident, now_str)
    else:
        subject = '%s - OK (%s)' % (options.ident, now_str)

    fn = os.path.join(options.log_dir, 'subject.txt')
    open(fn, 'w').write(subject)


    fn = os.path.join(options.log_dir, '..', 'index.rss')
    fp = open(fn, 'w')

    print >>fp, '<?xml version="1.0" encoding="iso-8859-1"?>'
    print >>fp, '<rss version="0.91">'
    print >>fp, '<channel>'
    print >>fp, '<title>Testrunner %s</title>' % options.ident
    print >>fp, '<link>%s/index.rss</link>' % options.base_url
    print >>fp, '<language>en</language>'

    for item in collect_rss(options):
        print >>fp, '\t<item>'

        subject_file = os.path.join(options.log_root, item, 'subject.txt')
        if os.path.exists(subject_file):
            print >>fp, '\t\t<title>%s</title>' % open(subject_file).read()
        else:
            print >>fp, '\t\t<title>Testrunner %s</title>' % item

        report_file = os.path.join(options.log_root, item, 'index.html')
        if os.path.exists(report_file):
            print >>fp, '\t\t<description><![CDATA[%s]]></description>' % open(report_file).read()

        print >>fp, '\t\t<link>%s/logs/%s/index.html</link>' % (options.base_url, item)
        print >>fp, '\t</item>'

    print >>fp, '</channel>'
    print >>fp, '</rss>'
    fp.close()

    return open(fn).read()


def db(results, options, tests_failed):

    from database.setup import setup

    if options.verbose:
        print 'Connection to %s' % options.dsn

    wrapper = setup(options.dsn)
    session = wrapper.session

    Testrunner, Run, Result = wrapper.getMappers('testrunner', 'run', 'result')
    # first we need a testrunner object
    rows = session.query(Testrunner).filter_by(name=unicode(options.ident)).all()

    if rows:
        TR = rows[0]
    else:
        TR = Testrunner(name=unicode(options.ident))
        session.save(TR)

    TR.last_run = now
    testrunner_id = TR.id

    # now we need a new Run object
    report_file = os.path.join(options.log_root, options.timestamp, 'index.html')
    description = None
    if os.path.exists(report_file):
        description = open(report_file).read()            

    tests_total = tests_passed = 0
    for k in sorted(results.keys()):
        tests_passed += (results[k]['number_tests'] - results[k]['number_failures'])
        tests_total += results[k]['number_tests']

    R = Run(created=datetime.now(),
            link='%s/logs/%s/index.html' % (options.base_url, options.timestamp),
            description=description,
            hostname=socket.gethostname(),
            run_ok=(tests_total==tests_passed),
            results_cumulated='%d/%d' % (tests_passed, tests_total),
            ipaddress=socket.gethostbyname(socket.gethostname()),
            creator=pwd.getpwuid(os.getuid())[00])

    session.save(R)

    for k in sorted(results.keys()):
        url = '%s/%s' % (options.base_url, results[k]['logfile']) 
        R.result.append(Result(module=unicode(k),
                        tests_passed=results[k]['number_tests'] - results[k]['number_failures'],
                        tests_total=results[k]['number_tests'],
                        tests_ok=results[k]['tests_ok'],
                        logfile=unicode(url),
                        logdata=open(results[k]['logfilepath']).read(),
                        ))

    # prune runs older than 7 days
    TR.run = [r for r in TR.run if (now - r.created).days < 7]
    TR.run.append(R)


    run_id = max([run.id for run in TR.run])
    #ugly i know 
    last_run_id = run_id + 1

    session.flush()
    session.commit()
    
    return testrunner_id, last_run_id
