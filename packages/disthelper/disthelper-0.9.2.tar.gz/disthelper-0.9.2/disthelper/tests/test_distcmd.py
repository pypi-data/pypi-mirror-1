
import os
import sys
from fixture import TempIO
from wikir.tests.shelldoc import find_shell_sessions, validate_session
test_dir = os.getcwd()
tmp = None

def setup():
    global tmp
    tmp = TempIO()
    os.chdir(tmp)

def teardown():
    # print >>sys.stderr, open(tmp.join('setup.py')).read()
    os.chdir(test_dir)

def test_docs():
    here = os.path.dirname(__file__)
    proj_path = os.path.join(here, '..', '..')
    f = open(os.path.join(proj_path, 'README.txt'), 'r')
    doc = f.read()
    f.close()
    for session in find_shell_sessions(doc):
        for i, line in enumerate(session):
            indent, token, cmd = line
            # print >>sys.stderr, indent, token, cmd
            # print >>sys.stderr, cmd
            if token=='$' and cmd.startswith('paster'):
                # shameless...
                cmd = "%s package=foo --no-interactive\n" % cmd.strip()
                # print >>sys.stderr, cmd
                session.lines[i] = (indent, token, cmd)
        yield validate_session, session