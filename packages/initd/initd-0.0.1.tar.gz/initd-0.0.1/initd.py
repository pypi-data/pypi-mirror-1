"""
Module to help with creation of initd scripts.

There are a couple ways to use this module.
* Explicitly use the start, stop, and restart functions to control a
  daemon from client code.
* Use the execute method to start a daemon from the command line, using
  the args to select the action from (start, stop, restart).

"""

from __future__ import with_statement

import logging, os, signal, sys, time

__all__ = ['start', 'stop', 'restart', 'execute']

def start(run, pid_file, log_file=None):
    """
    Starts the daemon.  This daemonizes the process, so the calling process
    will just exit normally.

    Arguments:
    * run:function - The command to run (repeatedly) within the daemon.
    * pid_file:str - The file path to store the running pid into.
    * log_file:str - The file path to log to.

    """
    from daemon import daemonize
    daemonize()

    _initialize_logging(log_file)
    _create_pid_file(pid_file)

    # workaround for closure issue is putting running flag in array
    running = [True]
    def cb_term_handler(sig, frame):
        """
        Invoked when the daemon is stopping.  Tries to stop gracefully
        before forcing termination.
        
        The arguments of this function are ignored, they only exist to
        provide compatibility for a signal handler.

        """
        running[0] = False
        def cb_alrm_handler(sig, frame):
            """
            Invoked when the daemon could not stop gracefully.  Forces
            exit.

            The arguments of this function are ignored, they only exist to
            provide compatibility for a signal handler.

            """
            logging.warn('Could not exit gracefully.  Forcefully exiting.')
            sys.exit(1)
        signal.signal(signal.SIGALRM, cb_alrm_handler)
        signal.alarm(5)

    signal.signal(signal.SIGTERM, cb_term_handler)

    logging.info('Starting')
    try:
        while running[0]:
            try:
                run()
            # disabling warning for catching Exception, since it is the
            # top level loop
            except Exception, exc: # pylint: disable-msg=W0703
                logging.exception(exc)
    finally:
        os.remove(pid_file)
        logging.info('Exiting.')


def stop(pid_file):
    """
    Stops the daemon.  This reads from the pid file, and sends the SIGTERM
    signal to the process with that as its pid.  This will also wait until
    the running process stops running.


    Arguments:
    * pid_file:str - The file path to store the running pid into.

    """
    with open(pid_file, 'r') as stream:
        pid = int(stream.read())
    sys.stdout.write('Stopping.')
    sys.stdout.flush()
    os.kill(pid, signal.SIGTERM)
    while os.path.exists(pid_file):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write('\n')


def restart(run, pid_file, log_file=None):
    """
    Restarts the daemon.  This simply calls stop (if the process is running)
    and then start again.

    Arguments:
    * run:function - The command to run (repeatedly) within the daemon.
    * pid_file:str - The file path to store the running pid into.
    * log_file:str - The file path to log to.

    """
    if os.path.exists(pid_file):
        stop(pid_file)
    print 'Starting.'
    start(run, pid_file, log_file)


def _initialize_logging(log_file):
    """
    Initializes logging if a log_file parameter is specified in config
    config.  Otherwise does not set up any log.
    
    Arguments:
    * log_file:str - The path to the log file, or None if no logging
                     should take place.

    """
    if log_file:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename=log_file,
                            filemode='w')


def _create_pid_file(pid_file):
    """
    Outputs the current pid to the pid file specified in config.  If the
    pid file cannot be written to, the daemon aborts.

    Arguments:
    * pid_file:str - The path to the pid file.

    """
    try:
        with open(pid_file, 'w') as stream:
            stream.write(str(os.getpid()))
    except OSError, err:
        logging.exception(err)
        logging.error('Failed to write to pid file, exiting now.')
        sys.exit(1)


def execute(run, pid_file, log_file=None):
    """
    Main entry point to the module.

    Arguments:
    * run:function - The command to run (repeatedly) within the daemon.
    * pid_file:str - The file path to store the running pid into.
    * log_file:str - The file path to log to.

    """
    cmds = {
        'start': start,
        'stop': lambda r, p, l: stop(pid_file),
        'restart': restart,
        }
    if len(sys.argv) < 2 or not sys.argv[1] in cmds.keys():
        print 'Usage: %s [%s]' % (sys.argv[0], '|'.join(cmds.iterkeys()))
        return

    cmd = cmds[sys.argv[1]]
    cmd(run, pid_file, log_file)
