##########################################################################
# haufe.testrunner
#
# (C) 2007, Haufe Mediengruppe
##########################################################################


import os
import sys
import re
import subprocess
import smtplib
import tempfile
import time
from datetime import datetime
from optparse import OptionParser
from ConfigParser import SafeConfigParser

import formatter

fp = sys.stdout

def testrunner(options, args):

    if not options.config:
        raise RuntimeError('No configuration specified')

    if not os.path.exists(options.config):
        raise RuntimeError('Configuration file %s does not exist' % options.config)

    CP = SafeConfigParser()
    CP.read([options.config])

    section = options.section
    sandbox_dir = CP.get(section, 'sandbox')
    options.ident = CP.get(section, 'ident')
    options.base_url = CP.get(section, 'base_url')
    options.dsn = None

    if CP.has_option(section, 'zope_start'):
        options.zope_start = CP.get(section, 'zope_start')
    else:
        options.zope_start = 'zopectl'

    if CP.has_option(section, 'runner_options'):
        options.runner_options = CP.get(section, 'runner_options')

    if CP.has_option(section, 'dsn'):
        options.dsn = CP.get(section, 'dsn')

    options.coverage = False
    if CP.has_option(section, 'coverage'):
        options.coverage = CP.getboolean(section, 'coverage')

    options.integration_tests = False
    if CP.has_option(section, 'integration_tests'):
        options.integration_tests = CP.getboolean(section, 'integration_tests')

    # ZEO options
    options.zeo_enabled = False
    if CP.has_section('zeo'):
        options.zeo_enabled = True
        options.zeo_host = CP.get('zeo', 'host')
        options.zeo_port = CP.get('zeo', 'port')

    # Selenium options
    options.selenium_enabled = False
    if CP.has_section('selenium'):
        options.selenium_enabled = True
        options.selenium_tr_host = CP.get('selenium', 'testrunner_host')
        options.selenium_tr_port = CP.get('selenium', 'testrunner_port')
        if CP.has_option('selenium', 'testrunner_https_port'):
            options.selenium_tr_https_port = CP.get('selenium', 'testrunner_https_port')
        else:
            options.selenium_tr_https_port = options.selenium_tr_port
        #options.selenium_instance_url = CP.get('selenium', 'instance_url')
        for opt in CP.options('selenium'):
            if opt.startswith('instance_url'):
                setattr(options, 'selenium_' + opt, CP.get('selenium', opt))

    tests = [t.strip() for t in CP.get(section, 'tests').replace('\n','').split(',')]

    # some sanity checks
    if not os.path.exists(sandbox_dir):
        raise RuntimeError('No sandbox found (%s)' % os.path.abspath(sandbox_dir))

    os.chdir(sandbox_dir)
    if not os.path.exists('bin/%s' % options.zope_start):
        raise RuntimeError('bin/%s not found' % options.zope_start)

    # prepare logging directory
    ts = datetime.now().strftime('%Y%m%dT%H%M%S')   
    options.timestamp = ts
    options.log_root = os.path.join(sandbox_dir, 'logs')
    options.log_relative_dir = os.path.join('logs', '%s' % ts)
    options.log_dir = os.path.join(sandbox_dir, 'logs', '%s' % ts)
    os.makedirs(options.log_dir)

    # update repository, if selected
    if options.update:
        update_repository(sandbox_dir, options)

    # restart instance
    if options.restart:
        restart_instance(sandbox_dir, options)

    results, tests_failed, num_tests = run_tests(sandbox_dir, tests, options)
    result_html = formatter.html(results, options)

    testrunner_id = run_id = None
    if options.rss:
        formatter.rss(results, options, tests_failed)

    if options.db:
        testrunner_id, run_id = formatter.db(results, options, tests_failed)
    result_text = formatter.text(results, options, testrunner_id, run_id)

    if options.clean:
        clean(options)

    if options.mail:
        if tests_failed > 0 :
            subject = '[%s] Testrunner FAILED :-(' % options.ident
            recipients = CP.get(section, 'email_failure')
        else:
            subject = '[%s] Testrunner OK :-)' % options.ident
            recipients = CP.get(section, 'email_ok')


        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText
        from email.MIMEImage import MIMEImage
        from email.Header import Header

        outer = MIMEMultipart()
        outer['From'] = 'ep-testrunner-no-reply@haufe.de'
        outer['To'] = recipients
        outer['Subject'] = subject
        outer['Content-Type'] = 'text/plain; charset=iso-8859-15'
        outer['Content-Disposition'] = 'inline; filename=report.txt'
        outer.attach(MIMEText(result_text, _charset='iso-8859-15'))

        if options.mail_with_html:
            part = MIMEText(result_html, _charset='iso-8859-15')
            part.add_header('content-type', 'text/html')
            part.add_header('Content-Disposition', 'inline; filename=index.html')
            outer.attach(part)

        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(outer['From'],
                      outer['To'].split(','),
                      outer.as_string())

        smtp.close()


def update_repository(sandbox_dir, options):
    """ CVS/SVN updates the related directories """

    for dirname in ('Products', 'lib/python', 'Base'):
        os.chdir(sandbox_dir)
        if os.path.exists(dirname):
            os.chdir(dirname)
            if os.path.exists('.svn'):
                repos_type = 'svn'
            elif os.path.exists('CVS'):
                repos_type = 'cvs'
            else:
                raise IOError('Could not determine repository type for %s' % dirname)

            if options.verbose:
                print >>fp, 'Updating %s' % os.path.abspath(os.getcwd())
            if repos_type == 'cvs':
                os.system('cvs -q update -dP')
            else:
                os.system('svn update')

def restart_instance(sandbox_dir, options):
    """ Restart Zope instance """

    os.chdir(sandbox_dir)
    os.system('bin/%s restart' % options.zope_start)
    if options.verbose:
        print >>fp, 'Zope instance restarted'


def clean(options):
    """ Clean up old logfiles (older than 2 weeks) """
        
    if options.verbose:
        print >>fp, 'Cleaning up old logs'

    for dirname in os.listdir(options.log_root):
        full_dirname = os.path.join(options.log_root, dirname)

        if not os.path.isdir(full_dirname):
            continue

        ctime = os.stat(full_dirname)[9]
        if ctime < time.time() - 24*3600*7:
            if options.verbose:
                print >>fp, '\tRemoving %s' % full_dirname
            shutil.rmtree(full_dirname)



ran_tests = re.compile('Ran (\d*) test', re.I|re.M|re.S)
errors = re.compile('FAILED.*?errors=(\d*)', re.I|re.M|re.S)
failures = re.compile('FAILED.*?failures=(\d*)', re.I|re.M|re.S)


def run_tests(sandbox_dir, tests, options):
    """ Run each test seperatly using zopectl test """

    def normalize(s):
        """ normalize a string """
        return s.lower().replace(os.path.sep, '_')

    # Optional support to run the testrunner against an existing
    # ZEO server instead of an empty DemoStorage (see Testing/custom_zodb.py)
    if options.zeo_enabled:
        os.environ['TEST_ZEO_HOST'] = options.zeo_host
        os.environ['TEST_ZEO_PORT'] = options.zeo_port
        if options.integration_tests:
            os.environ['INTEGRATION_TESTS'] = '1'

    # Setup Selenium environment variables (used by SeleniumTestcase)
    if options.selenium_enabled:
        os.environ['SELENIUM_HOST'] = options.selenium_tr_host 
        os.environ['SELENIUM_PORT'] = options.selenium_tr_port 
        os.environ['SELENIUM_HTTPS_PORT'] = options.selenium_tr_https_port 
        #os.environ['SELENIUM_INSTANCE_URL'] = options.selenium_instance_url 
        for attr in vars(options):
            if attr.startswith('selenium_instance_url'):
                os.environ[attr.upper()] = getattr(options, attr)

    os.chdir(sandbox_dir)
    results = {}

    tests_failed = 0
    for test in tests:
        
        tempf = tempfile.mktemp()
        cmd = ''
        if hasattr(options,'runner_options'):
            # -s, --bla foo, --foo=bar.foo
            # first parameter is used for package it shoud be '--listdir' or '-s'
            runner_options = options.runner_options
            cmd = 'bin/%s 1>%s 2>&1 test %s %s %s' % (options.zope_start, tempf, 
                                                      ''.join(runner_options.split(',')[1:]),
                                                      ''.join(runner_options.split(',')[:1]), test)
        else:
            runner_options = ['-vvv']
            if options.coverage:
                runner_options.append('-T')
            cmd = 'bin/%s 1>%s 2>&1 test %s --libdir %s' % (options.zope_start, tempf, ' '.join(runner_options), test)

        if options.verbose:
            print >>fp, 'Executing %s' % cmd
        status = os.system(cmd)
        log = open(tempf).read()

        d = {}         
        # now parse the logs
        # search for 'Ran N tests'
        mo = ran_tests.search(log)
        if mo:
            d['number_tests'] = int(mo.group(1))    
        else:
            d['number_tests'] = 0

        # check for errors=XXXX...
        d['number_failures'] = 0
        d['tests_ok'] = True

        mo_e = errors.search(log)
        mo_f = failures.search(log)

        if mo_e or mo_f:
            tests_failed += 1
            d['tests_ok'] = False                        
            if mo_e: d['number_failures'] += int(mo_e.group(1))
            if mo_f: d['number_failures'] += int(mo_f.group(1))


        # write test specific logfile
        fn = os.path.join(options.log_dir, normalize(test) + '.txt')
        open(fn, 'w').write(log)
        d['logfile'] = os.path.join(options.log_relative_dir, normalize(test) + '.txt')
        d['logfilepath'] = fn

        if options.verbose:
            print >>fp, log

        results[test] = d
        if options.verbose:
            print >>fp, d

    return results, tests_failed, len(tests)


def main():

    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true",
                      default=False, help='Verbose mode on')

    parser.add_option('-u', '--update', dest='update', action='store_true',
                      default=False,
                      help='SVN/CVS update sandbox before running the tests')

    parser.add_option('-c', '--config', dest='config',
                      help='Path to configuration file')

    parser.add_option('-m', '--mail', dest='mail', action="store_true",
                      default=False,
                      help='Mail results')

    parser.add_option('-d', '--db', dest='db', action="store_true",
                      default=False,
                      help='Store results in database')

    parser.add_option('-l', '--mail-with-html', dest='mail_with_html', action="store_true",
                      default=False,
                      help='Include HTML report in mail notification')

    parser.add_option('-z', '--restart', dest='restart', action="store_true",
                      default=False,
                      help='Restart the Zope instance (necessary for Selenium tests)')

    parser.add_option('-r', '--rss', dest='rss', action="store_true",
                      default=False,
                      help='Generate or update RSS feed')

    parser.add_option('-n', '--clean', dest='clean', action="store_true",
                      default=False,
                      help='Cleanup old logs (older than one week)')

    parser.add_option('-s', '--section', dest='section', default='default',
            help='Section to be taken from configuration file (Default: "default")')

    parser.add_option('-t', '--stylesheet', dest='stylesheet', default=None,
                      help='Optional path to a stylesheet (used within the generated HTML report)')

    parser.add_option('-V', '--version', dest='version', action='store_true',
                      default=False,
                      help='Show version info about haufe.testrunner package')

    (options, args) = parser.parse_args()

    if options.version:
        show_version()
    else:
        testrunner(options, args)


def show_version():

    import pkg_resources
    print >>fp, pkg_resources.require('haufe.testrunner')[0]
        
if __name__ == '__main__':
    main()
