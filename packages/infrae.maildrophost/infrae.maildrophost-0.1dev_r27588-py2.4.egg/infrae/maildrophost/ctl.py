

import os, signal, sys


def maildrop_start(config):
    mconfig = os.path.join(config['base'], 'config.py')
    mscript = os.path.sep.join(('maildrop', 'maildrop.py'))
    mscript = os.path.join(config['base'], mscript)
    os.execlp(sys.executable, sys.executable, mscript, mconfig)

def maildrop_stop(config):
    pid = int(open(config['pidfile']).read())
    os.kill(pid, signal.SIGTERM)
    os.unlink(config['pidfile'])
    print 'Stop %d daemon.' % pid


def main(config, action=None):
    if action:
        if action[0] == 'start':
            maildrop_start(config)
        elif action[0] == 'stop':
            maildrop_stop(config)
        elif action[0] == 'restart':
            maildrop_stop(config)
            maildrop_start(config)
        

    
