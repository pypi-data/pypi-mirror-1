import signal
import logging
from z3c.deadlockdebugger.threads import dump_threads

logger = logging.getLogger("Products.signalstack")

def showStacks(signal, stack):
    dt = dump_threads()
    logger.error(dt)

def initialize(contxt):
    signal.signal(signal.SIGUSR1, showStacks)
