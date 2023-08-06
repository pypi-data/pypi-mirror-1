#!/usr/bin/env python
from optparse import OptionParser
from subprocess import Popen, PIPE
import os, os.path
import signal, time
from datetime import datetime
from random import choice
import re

def main():
    timeout = 30
    usage = "usage: %prog [options] url-for-stub project-name"
    parser = OptionParser(usage=usage, version="%prog 0.1")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Incorrect number of arguments")

    # 1.0 Export the project from svn
    start = datetime.now()
    svn_process = Popen(['svn', 'export', args[0], args[1]], stdout=PIPE, stderr=PIPE)
    while svn_process.poll() is None:
        time.sleep(0.1)
        now = datetime.now()
        if (now - start).seconds > timeout:
            os.kill(svn_process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            parser.error("%s timed out " % args[0])
    
    # 2.0 Create the secret hash just like Django does
    settings_file = os.path.join(os.getcwd(), args[1], 'settings.py')
    print settings_file
    settings_content = open(settings_file, 'r').read()
    fp = open(settings_file, 'w')
    secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    settings_content = re.sub(r"(?<=SECRET_KEY = ')'", secret_key + "'", settings_content)
    fp.write(settings_content)
    fp.close()
    
    print "'%s' created" % args[1]
    
if __name__ == "__main__":
    main()
    