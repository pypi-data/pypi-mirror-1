
"""Nose plugin to run your test suite in multiple versions of Python simultaneously."""

import os
import time
import re
import logging
import sys
try:
    import cPickle as pickle
except ImportError:
    import pickle

from nose.plugins.base import Plugin
from nose.core import TextTestRunner
from nose import loader
from nose import failure
import execnet

log = logging.getLogger(__name__)
major_version_pattern = re.compile(r'\d\.\d')

process_is_worker = False

class MultiVersion(Plugin):
    """Run tests simultaneously in different versions of Python."""
    name = 'multiversion'
    score = 1 # must come after worker
    
    def options(self, parser, env=os.environ):
        super(MultiVersion, self).options(parser, env)
        parser.add_option(
            '--in-python', dest="in_pythons", default=[], action="append",
            help=('Major version or path of Python interpreter to run tests in. '
                  'Example value: 2.4,2.5,2.6,/path/to/your-virtualenv/bin/python. '
                  'Option can be specified multiple times.'))

    def configure(self, options, config):
        super(MultiVersion, self).configure(options, config)
        self.config = config
        self.options = options
        if len(self.options.in_pythons):
            self.enabled = True
        if process_is_worker:
            # main plugin cannot be active for a worker process
            self.enabled = False
        if not self.enabled:
            return
        in_pythons = []
        for p in self.options.in_pythons:
            p = p.strip()
            expanded_values = []
            if "\n" in p:
                # multi-line config value:
                expanded_values.extend(p.split("\n"))
            else:
                expanded_values.append(p)
            for path in expanded_values:
                in_pythons.extend(path.split(','))
        log.debug(repr(in_pythons))
        self.in_pythons = expand_pythons(in_pythons)
        self.nosetests_args = []
        for a in sys.argv:
            # TODO(kumar) get args programmatically from nose
            if '--with-multiversion' in a:
                # skip self activation arg
                continue
            if '--in-python' in a:
                continue
            self.nosetests_args.append(a)

    def prepareTestLoader(self, loader):
        # remember loader for test runner
        self.loaderClass = loader.__class__

    def prepareTestRunner(self, runner):
        # replace with our runner class
        return MultiVersionTestRunner(stream=runner.stream,
                                      verbosity=self.config.verbosity,
                                      config=self.config,
                                      loaderClass=self.loaderClass,
                                      in_pythons=self.in_pythons,
                                      nosetests_args=self.nosetests_args)

class MultiVersionTestRunner(TextTestRunner):

    def __init__(self, **kw):
        self.loaderClass = kw.pop('loaderClass', loader.defaultTestLoader)
        self.in_pythons = kw.pop('in_pythons')
        self.nosetests_args = kw.pop('nosetests_args')
        super(MultiVersionTestRunner, self).__init__(**kw)

    def run(self, test):
        result = self._makeResult()
        start = time.time()
        
        workers = []
        for python in self.in_pythons:
            workers.append(
                execnet.makegateway("popen//python=%s" % python)
            )
        log.debug("workers: %r" % workers)
        
        # start the test suites
        worker_channels = []
        for w in workers:
            log.debug("Sending args to %s %r" % (w, self.nosetests_args))
            worker_channels.append(w.remote_exec("""
                import nose
                from nosemultiversion import MultiVersionWorker
                # channel is a magic global set by execnet
                nose.run(argv=%r, addplugins=[MultiVersionWorker(enabled=True, channel=channel)])
                """ % self.nosetests_args))
        
        num_running = len(workers)
        while num_running > 0:
            for ch in worker_channels:
                log.debug("receiving from %s" % ch)
                try:
                    remote_results = ch.receive()
                except EOFError:
                    num_running -= 1
                    continue
                else:
                    # each list of results makes up one test.
                    # e.g. result.startTest(), 
                    #      result.addSuccess(), 
                    #      result.stopTest()
                    for remote_action, remote_action_args in remote_results:
                        action = getattr(result, remote_action)
                        action(*pickle.loads(remote_action_args))

        stop = time.time()

        result.printErrors()
        result.printSummary(start, stop)
        self.config.plugins.finalize(result)

        return result

class MultiVersionWorker(Plugin):
    name = 'multiversion_worker'
    score = 99 # must come before main plugin
    
    def __init__(self, enabled=False, channel=None):
        self.enabled = enabled
        self.channel = channel
        super(MultiVersionWorker, self).__init__()
    
    def options(self, parser, env=os.environ):
        # super(MultiVersionWorker, self).options(parser, env)
        pass

    def configure(self, options, config):
        global process_is_worker
        super(MultiVersionWorker, self).configure(options, config)
        if not self.enabled:
            return
        
        process_is_worker = True
        log.debug("worker: curr dir: %s" % os.getcwd())
        
        self.worker_id = self.get_worker_id()
    
    def get_worker_id(self):
        exec_dirs = sys.executable.split(os.path.sep)
        if len(exec_dirs) == 1:
            # maybe Windows?
            return sys.executable
            
        if exec_dirs[-2] == 'bin':
            # e.g. my-venv/bin/python or local/bin/python
            return os.path.sep.join(exec_dirs[-3:])
        elif exec_dirs[-2] == 'MacOS':
            # e.g. 2.6/Resources/Python.app/Contents/MacOS/Python
            # -->  2.6/../Python
            return os.path.sep.join([exec_dirs[-6], '...', exec_dirs[-1]])
        else:
            # unknown
            return sys.executable
    
    def addError(self, test, err):
        err = flatten_err(err)
        self.queue.append(
            ('addError', pickle.dumps(tuple([TestLet(test, self.worker_id), err])))
        )
    
    def addFailure(self, test, err):
        err = flatten_err(err)
        self.queue.append(
            ('addFailure', pickle.dumps(tuple([TestLet(test, self.worker_id), err])))
        )
        
    def addSuccess(self, test):
        self.queue.append(
            ('addSuccess', pickle.dumps(tuple([TestLet(test, self.worker_id)])))
        )
        
    def startTest(self, test):
        self.queue = [] # reset
        self.queue.append(
            ('startTest', pickle.dumps(tuple([TestLet(test, self.worker_id)])))
        )
        
    def stopTest(self, test):
        self.queue.append(
            ('stopTest', pickle.dumps(tuple([TestLet(test, self.worker_id)])))
        )
        self.channel.send(self.queue)
    
    def setOutputStream(self, stream):
        # return dummy stream to stop the worker 
        # from reporting like normal Nose
        class dummy:
            def flush(self, *args):
                pass
            def write(self, *arg):
                pass
            def writeln(self, *arg):
                pass
        d = dummy()
        return d
        
class TestLet(object):
    """A test case object that can be pickled.
    
    This code originally lived in nose.plugins.multiprocess but 
    has been updated for a few extra attributes that were needed.
    """
    
    def __init__(self, case, worker_id):
        try:
            self._id = case.id()
        except AttributeError:
            pass
        self._str = str(case)
        self._short_description = "%s: %s" % (worker_id, case.shortDescription() or self._str)
        if hasattr(case, 'failureException'):
            self.failureException = case.failureException

    def id(self):
        return self._id

    def shortDescription(self):
        return self._short_description

    def __str__(self):
        return self._str
        
def flatten_err(err):
    """Flatten a sys.exc_info() tuple so it can be pickled."""
    etype, val, tb = err
    flat_tb = FlatTraceback(tb)
    return (etype, val, flat_tb)

class FlatTraceback(object):
    """A traceback object that can be pickled."""
    
    def __init__(self, tb):
        self.tb_frame = FlatTracebackFrame(tb.tb_frame)
        self.tb_lasti = tb.tb_lasti
        self.tb_lineno = tb.tb_lineno
        self.tb_next = tb.tb_next and FlatTraceback(tb.tb_next)

class FlatTracebackFrame(object):
    """A traceback's frame object that can be pickled."""
    
    def __init__(self, tb_frame):
        self.f_code = FlatFrameCode(tb_frame.f_code)
        # nullifying globals here has the effect of 
        # destroying any custom __loader__ objects that 
        # linecache would otherwise use.
        self.f_globals = {}

class FlatFrameCode(object):
    """A traceback's frame code object that can be pickled."""
    
    def __init__(self, f_code):
        self.co_filename = f_code.co_filename
        self.co_name = f_code.co_name

def expand_pythons(python_options):
    """Take a list of python specs and return a list 
    of absolute paths to those interpreters.
    
    A "spec" is either a major version number (e.g. 2.6) or 
    an absolute path to an interpreter.
    """
    pythons = []
    for spec in python_options:
        if major_version_pattern.match(spec):
            pythons.append(which_python(spec))
        else:
            # assume it's a path to a python version:
            pythons.append(spec) 
    return pythons

def which_python(version):
    """Given a major version of Python, return the 
    absolute path to that interpreter.
    """
    bin = "python%s" % version
    for path in os.environ['PATH'].split(":"):
        possible_bin = os.path.join(path, bin)
        if os.path.exists(possible_bin):
            return possible_bin
            
    raise OSError("Unable to locate %s in $PATH" % bin)
