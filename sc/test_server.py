"""SuttaCentral test server environment for production.

Usage: cherryd -i sc.test_server

Note: This module is not intended to be imported from another module or
program.

This module will do much the same as sc.server, but instead it runs
on another port, confirms that pages return a HTTP 200 response,
performs git rollback and rollforward to deal with problems.
If this returns with an exit code of 0, it is strongly indicitive that
the production server will start up and run without serious problems.
An exit code of 1 almost guarantees there will be serious problems.
"""
import os
import json
import time
import logging
import threading
import urllib.parse
import urllib.request
logger = logging.getLogger(__name__)

done = threading.Event()

def start_server():
    sc.config['app']['log_level'] = 'ERROR'
    app.setup()
    sc.config['global']['server.socket_port'] = sc.config['test']['port']
    app.mount()

def test_server():
    base_url = 'http://{host}:{port}'.format(**sc.config['test'])
    attempts = 0
    max_attempts = 2
    time.sleep(0.1)
    print('Now loading test pages to confirm server stability')
    while attempts < max_attempts:
        if attempts != 0:
            time.sleep(4)
        attempts += 1
        
        try:
            for path in sc.config['test']['paths']:
                url = urllib.parse.urljoin(base_url, path)
                response = urllib.request.urlopen(url)
                print('{} [{}]'.format(url, response.code))
                if response.code == 200:
                    continue
                else:
                    break
            # Success!
            stop(0)
                
        except urllib.error.URLError as e:
            print('{} : {!s}'.format(url, e))
    
    print(_red_text('Failed to achieve a 200 response for {}'.format(url)))
    stop(1)

def save_last_good():
    import sc.scm
    with open(sc.config['test']['last_good_rev_file'], 'w') as f:
        json.dump({
                'code': sc.scm.scm.last_commit_revision,
                'data': sc.scm.data_scm.last_commit_revision
            }, f)

def roll_back():
    import sc.scm
    try:
        with open(sc.config['test']['last_good_rev_file'], 'r') as f:
            revs = json.load(f)
    except FileNotFoundError:
        print('Unable to rollback')
        return False
    sc.scm.scm.checkout(revs['code'])
    sc.scm.data_scm.checkout(revs['data'])
    print('Successfully rolled back to last known good state')

def roll_forward():
    import sc.scm
    sc.scm.scm.checkout(sc.config['test']['branch'] or 'master')
    sc.scm.data_scm.checkout(sc.config['test']['branch'] or 'master')

def stop(exit_code):
    print('Now shutting down server')
    cherrypy.engine.exit()
    cherrypy.server.stop()
    time.sleep(0.5)
    if exit_code == 0:
        print(_green_text('''\
Test Server returns HTTP 200 Responses. Production should be good to go.'''))
        save_last_good()
    else:
        roll_back()
        print(_red_text('''\
CRITICAL PROBLEM! [AKA Bad Dev, Don't break the server!]
A test instance of the server using the current branch code
fails to generate HTTP 200 Responses. This is a critical problem causing
all or much of the site to generate error pages instead of the intended
pages.
Please attempt to reproduce this problem on a development server
or the staging server.
The production server has not been restarted and is still running the
pre-updated code. It should still be functioning correctly especially
if the rollback succeeded.
However it may be in an inconsistent state or generating errors.
If you are unable to fix the problem, please inform the primary server
administrator that this problem has occurred.
This warning should not be bypassed as if the production server is 
restarted now it will almost certainly be severely broken.
'''))
    os._exit(exit_code)

def _green_text(text):
    try:
        from colorama import Fore
        return Fore.GREEN + text + Fore.RESET
    except ImportError:
        return text

def _red_text(text):
    try:
        from colorama import Fore
        return Fore.RED + text + Fore.RESET
    except ImportError:
        return text
    
try:
    import sc
    from sc import app, updater
    import cherrypy
    
    roll_forward()
    start_server()
    
    t = threading.Thread(target=test_server)
    t.start()

except ImportError as e:
    logger.exception(e)
    cmd = 'pip install -r requirements.txt'
    logger.error('Missing dependency, try running: {}'.format(_green_text(cmd)))
    exit(1)
    
    
