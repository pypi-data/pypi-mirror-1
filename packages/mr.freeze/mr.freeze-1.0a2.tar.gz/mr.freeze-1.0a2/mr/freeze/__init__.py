import os
import re
import signal
import sys
import logging
import string
logger = logging.getLogger('mr.freeze')

from App.config import getConfiguration
from mr.freeze.freeze import set_freeze

def initialize(context):
    import patches
    logger.info('Patched ZPublisher.Publish.call_object')
    signal.signal(signal.SIGUSR1, handleSignal)
    logger.info('Installed USR1 signal handler')

def getFreezeFileName():
    cfg = getConfiguration()
    fname, ext = os.path.splitext(cfg.pid_filename)
    return fname + '.freeze'

def readCommands():
    freeze_filename = getFreezeFileName()
    try:
        freeze_file = open(freeze_filename, 'r')
        cmds = freeze_file.readlines()
        freeze_file.close()
        return map(string.strip, cmds)
    except IOError:
        logger.warn('Unable to read freeze file %s' % freeze_filename)
        return None

freeze_re = re.compile(r'^freeze\s+(.+)\s+(\d+)$')
def handleSignal(signal, stack):
    for cmd in readCommands():
        freeze_match = freeze_re.match(cmd)
        if cmd == 'pony':
            showPony()
        elif cmd == 'freeze':
            logger.info('Preparing to freeze')
            set_freeze()
        elif freeze_match:
            filename, lineno = freeze_match.group(1, 2)
            filename = os.path.realpath(filename)
            lineno = int(lineno)
            logger.info('Preparing to freeze at %s line %s' % (filename, lineno))
            set_freeze(filename=filename, lineno=lineno)
        elif cmd == 'stack' or cmd is None: # default
            showStacks()
        else:
            logger.warn('Unrecognized command: %s' % cmd)

### Commands ###

from z3c.deadlockdebugger.threads import dump_threads
def showStacks():
    print dump_threads()
    sys.stdout.flush()

def showPony():
    print """
            .,,.
         ,;;*;;;;,
        .-'``;-');;.
       /'  .-.  /*;;
     .'    \d    \;;               .;;;,
    / o      `    \;    ,__.     ,;*;;;*;,
    \__, _.__,'   \_.-') __)--.;;;;;*;;;;,
     `""`;;;\       /-')_) __)  `\' ';;;;;;
        ;*;;;        -') `)_)  |\ |  ;;;;*;
        ;;;;|        `---`    O | | ;;*;;;
        *;*;\|                 O  / ;;;;;*
       ;;;;;/|    .-------\      / ;*;;;;;
      ;;;*;/ \    |        '.   (`. ;;;*;;;
      ;;;;;'. ;   |          )   \ | ;;;;;;
      ,;*;;;;\/   |.        /   /` | ';;;*;
       ;;;;;;/    |/       /   /__/   ';;;
       '*jgs/     |       /    |      ;*;
            `""""`        `""""`     ;'
"""
    sys.stdout.flush()
