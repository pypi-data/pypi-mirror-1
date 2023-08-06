"""PyLint Plugin"""

import logging
import unittest
import sys
from StringIO import StringIO

from pylint import lint
from pylint import checkers
from pylint.reporters.text import TextReporter
from pylint.interfaces import IReporter

from nose.plugins import Plugin
from nose.plugins.errorclass import ErrorClassPlugin, ErrorClass


log = logging.getLogger('nose.plugins')


class LintError(Exception):
    """The LintError wraps PyLint messages"""

    def __init__(self, filename, messages):
        Exception.__init__(self)
        self.filename = filename
        self.messages = messages

    def imitation_traceback(self):
        """Provide an imitation traceback, but with lint errors"""
        
        buf = StringIO()
        buf.write("PyLint analysis:\n")

        (msg_id,
             (filename, modname, objname, lineno),
             message) = self.messages[0]
        buf.write('  File "%(filename)s"\n' % locals())
                
        for (msg_id,
             (filename, modname, objname, lineno),
             message) in self.messages:
            buf.write('    %(msg_id)s: '
                      '%(lineno)s: '
                      '%(objname)s: '
                      '%(message)s\n'
                      % locals())

        return buf.getvalue()


# monkey patch unittest._TextTestResult
original_exc_info_as_string = unittest._TextTestResult._exc_info_to_string

def _exc_info_to_string(self, err, test=None):
    """for lint errors we provide a custom traceback, otherwise upcall"""
    if err[0] == LintError:
        return err[1].imitation_traceback()
    else:
        return original_exc_info_as_string(self, err, test)

unittest._TextTestResult._exc_info_to_string = _exc_info_to_string



class LintTestCase(unittest.TestCase):
    """This test case is yielded per module with the lint messages"""
        
    def __init__(self, module, messages):
        unittest.TestCase.__init__(self, methodName='lint')
        self.messages = messages
        self.module = module
        self._testMethodDoc = "PyLint test of %s" % module.__name__

    
    def lint(self):
        """raise a LintError if we have any messages"""
        if self.messages:
            raise LintError(self.module.__file__, self.messages)

        

class PyLintPlugin(ErrorClassPlugin):
    """Plugin that provides PyLint features for nose.

       The plugin creates one test case per module that wraps
       all the PyLint messages.  This fails if the messages are
       non empty.

       At the end of the run, it re-runs lint on all the files it has
       seen to create the gloabl metrics report from lint
       """
    
    
    name = "pylint"
    enableOpt = "not sure why this attribute is needed"

    linterror = ErrorClass(LintError, label='LINT', isfailure=True)

    to_check = None

    def __init__(self):
        ErrorClassPlugin.__init__(self)
        self.to_check = []
        self.messages = None
        
        self.linter = linter = lint.PyLinter()
        
        # initialize checkers
        checkers.initialize(linter)

        # handle config file
        if True:
            linter.read_config_file()
            config_parser = linter._config_parser
            if config_parser.has_option('master', 'load-plugins'):
                plugins = get_csv(config_parser.get('master', 'load-plugins'))
                linter.load_plugin_modules(plugins)
            linter.load_config_file()

        linter.reporter = self

    def loadTestsFromModule(self, module):
        """append to the list of filenames for at report time"""

        # store the file for a deferred check
        self.to_check.append(module.__file__)

        # capture any messages associated with this file and yield a case
        self.messages = []
        self.linter.check(module.__file__)
        return [LintTestCase(module, self.messages)]
        

    def wantFile(self, filename):
        """this plugin wants all python files"""
        if filename.endswith('.py'):
            return True

    def report(self, stream):
        """run linter on all the files we collected"""

        if not self.to_check:
            # don't bother if no files were found
            return

        reporter = TextReporter(stream)
        self.linter.reporter = reporter
        self.linter.check(self.to_check)
            

    # PyLint IReporter interface
    __implements__ = IReporter

    def add_message(self, msg_id, location, msg):
        """collect messages so they can be returned as a LintTestCase"""
        log.info("pylint add_message %s" % msg_id)
        self.messages.append((msg_id, location, msg))

    def display_results(self, layout):
        """do not display results"""
        pass


class TestPyLintPlugin(unittest.TestCase):

    plugin = None
    collected_tests = None

    def setUp(self):
        if TestPyLintPlugin.plugin is None:
            TestPyLintPlugin.plugin = PyLintPlugin()
            TestPyLintPlugin.collected_tests = self.plugin.loadTestsFromModule(
                sys.modules[__name__]
                )
        
    def test_creates_a_pylint_report(self):
        # create report 
        buf = StringIO()
        self.plugin.report(buf)
        report =  buf.getvalue()

        # check it looks like a pylint report 
        assert 'Report' in report
        assert 'statements analysed' in report
        assert 'External dependencies' in report 
        
    def test_yields_one_test_per_file(self):
        assert len(self.collected_tests) == 1

    def test_yields_LintTestCase(self):
        assert isinstance(self.collected_tests[0], LintTestCase)


class TestLintTestCase(unittest.TestCase):
    
    def test_pylint_messages_cause_lint_method_to_raise_LintError(self):
        # no messages is fine
        err = LintTestCase(sys.modules[__name__], [])
        err.lint()

        # some messages cause an exception
        err = LintTestCase(sys.modules[__name__], [True])
        self.assertRaises(LintError, err.lint)
        
