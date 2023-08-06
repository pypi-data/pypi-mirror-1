import signal
import sys
from z3c.deadlockdebugger.threads import dump_threads


def showStacks(signal, stack):
    print dump_threads()
    sys.stdout.flush()


def initialize(contxt):
    signal.signal(signal.SIGUSR1, showStacks)


