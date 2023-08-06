"""Plugin for the nose testing framework to list tests without running them.

Use ``nosetests --list-test-names`` or ``nosetests --list-long-test-names`` to
enable the plugin.  The latter gives long names that can be used as arguments
to nosetests (this won't work as expected if you use --doctest-tests).

Copyright 2008 John J. Lee <jjl@pobox.com>
"""

import logging
import os
import unittest

import nose.case
import nose.plugins
import nose.proxy
import nose.suite

__version__ = "0.2a"
__revision__ = "$Id: $"

log = logging.getLogger(__name__)


def normalize_path(pathname):
    if hasattr(os.path, "realpath"):
        pathname = os.path.realpath(pathname)
    return os.path.normcase(os.path.abspath(pathname))


def relative_location(basedir, target, posix_result=True):
    """
    >>> relative_location("/a/b/", "/a/b/c")
    'c'
    >>> relative_location("a/b", "a/b/c/d")
    'c/d'
    >>> relative_location("/z", "/a/b")
    '../a/b'

    >>> this_dir = os.path.dirname(normalize_path(__file__))
    >>> relative_location("/a/b/", "a/b/c") == "../.." + this_dir + "/a/b/c"
    True

    >>> nr_dirs_up_to_root = os.path.join(this_dir, "a", "b").count(os.sep)
    >>> expected = "/".join([".."] * nr_dirs_up_to_root) + "/a/b/c/d"
    >>> relative_location("a/b", "/a/b/c/d/") == expected
    True
    """
    # based on a function by Robin Becker
    import os.path, posixpath
    basedir = normalize_path(basedir)
    target = normalize_path(target)
    baseparts = basedir.split(os.sep)
    targetparts = target.split(os.sep)
    nr_base = len(baseparts)
    nr_target = len(targetparts)
    nr_common = min(nr_base, nr_target)
    ii = 0
    while ii < nr_common and baseparts[ii] == targetparts[ii]:
        ii += 1
    relative_parts = (nr_base-ii)*['..'] + targetparts[ii:]
    if posix_result:
        return posixpath.join(*relative_parts)
    else:
        return os.path.join(*relative_parts)


class FixturelessSuite(nose.suite.LazySuite):

    """Suite that does not run fixtures."""

    def __init__(self, tests, config, resultProxyFactory):
        nose.suite.LazySuite.__init__(self, tests)
        self._resultProxyFactory = resultProxyFactory
        self._config = config

    def run(self, result):
        result, orig = self._resultProxyFactory(result, self), result
        for test in self._tests:
            if result.shouldStop:
                log.debug("stopping")
                break
            # each nose.case.Test will create its own result proxy
            # so the cases need the original result, to avoid proxy
            # chains
            test(orig)

    def _get_wrapped_tests(self):
        for test in self._get_tests():
            if (isinstance(test, nose.case.Test) or
                isinstance(test,unittest.TestSuite)):
                yield test
            else:
                yield nose.case.Test(test,
                           config=self._config,
                           resultProxy=self._resultProxyFactory)

    _tests = property(_get_wrapped_tests, nose.suite.LazySuite._set_tests,
                      None, "")


class SuiteFactory(object):

    def __init__(self, config, suiteClass, resultProxyFactory):
        self._config = config
        self._suiteClass = suiteClass
        self._resultProxyFactory = resultProxyFactory

    def __call__(self, tests):
        return self._suiteClass(tests, self._config, self._resultProxyFactory)


class TestListingPlugin(nose.plugins.Plugin):

    """Only list test names, don't actually run any tests."""

    class _StopThisTest(Exception):
        pass

    def options(self, parser, env=os.environ):
        env_opt = "NOSE_LIST_TEST_NAMES"
        parser.add_option("--list-test-names",
                          action="store_true",
                          dest=self.enableOpt,
                          default=env.get(env_opt),
                          help="Enable plugin %s: %s [%s]" %
                          (self.__class__.__name__, self.help(), env_opt))
        parser.add_option("--list-long-test-names", action="store_true",
                          dest="list_long_test_names",
                          default=False,
                          help="Like --list-test-names, but use long names "
                               "that can be used as arguments to nosetests "
                               "(this won't work as expected if you use "
                               "--doctest-tests)")

    def configure(self, options, conf):
        nose.plugins.Plugin.configure(self, options, conf)
        self._list_long_test_names = options.list_long_test_names
        if self._list_long_test_names:
            self.enabled = True

    # XXX: .prepareTestLoader() and .setOutputStream() aren't guaranteed to
    # work:
    # http://code.google.com/p/python-nose/issues/detail?id=168

    def prepareTestLoader(self, loader):
        proxy_factory = nose.proxy.ResultProxyFactory(config=self.conf)
        loader.suiteClass = SuiteFactory(self.conf, FixturelessSuite,
                                         proxy_factory)

    def setOutputStream(self, stream):
        self.stream = stream

    def _name_from_address(self, address):
        filename, module, call = address
        if filename is not None:
            if filename[-4:] in [".pyc", ".pyo"]:
                filename = filename[:-1]
            head = relative_location(os.getcwd(), filename, posix_result=False)
        else:
            head = module
        if call is not None:
            return "%s:%s" % (head, call)
        return head

    def _test_name(self, test):
        if self._list_long_test_names:
            return self._name_from_address(test.address())
        else:
            return test.shortDescription() or str(test)

    def beforeTest(self, test):
        self.stream.writeln(self._test_name(test))
        raise TestListingPlugin._StopThisTest()

    def handleError(self, test, err):
        if issubclass(err[0], TestListingPlugin._StopThisTest):
            return True
