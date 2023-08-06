import signal
from z3c.deadlockdebugger.threads import dump_threads


def showStacks(signal, stack):
    print dump_threads()


def initialize(contxt):
    signal.signal(signal.SIGUSR1, showStacks)


