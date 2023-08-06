import os
import sys
import unittest

def alltests(start, start_modname, **kwargs):
    """ Create a TestSuite out of all modules in directory start relative to
    module name start_modname.

    Example creating a suite out all test modules beneath the myapp.tests
    module:

    myapp/tests/__init__.py:

        >>> def suite():
        ...     return alltests(__file__, __name__)
    """
    return DepthTestFinder(*args, **kwargs).alltests()

class DepthTestFinder(object):
    """ Find all test modules in a package """

    suite = unittest.TestSuite()
    testloader = unittest.defaultTestLoader.loadTestsFromModule
    suite_testlist_attr = "_tests"
    suite_add_test_funcname = "addTest"

    def __init__(self, start, start_modname, **kwargs):
        """ start is the directory to start finding in.
            start_modname is the name of the module the modules we find are
            relative to.  """
        self.start = os.path.dirname(start)
        self.start_modname = start_modname
        self.suite = kwargs.get("suite", self.suite)
    
    def alltests(self):
        """ Execute the search and return results as a unittest suite """
        [self.add_tests_from_module_name(module_name)
            for module_name in self.iterfindmodules()]
        return self.suite

    def add_test(self, test):
        """ Add a test to the suite """
        addtest_func = getattr(self.suite, self.suite_add_test_funcname)
        addtest_func(test)

    def path_to_module(self, path):
        """ Convert a path to a Python module name """
        path = path.strip(os.path.sep)
        path = path.replace(".py", "")
        path = path.replace(os.path.sep, ".")
        return path

    def dir_is_test_module(self, dirname, root):
        """ Test if the directory is a test module """
        is_module = os.path.exists(os.path.join(root, dirname, "__init__.py"))
        return dirname.startswith("test") and is_module
    
    def file_is_test_module(self, filename):
        """ Test if the file is a test module """
        return filename.startswith("test") and filename.endswith(".py")

    def add_tests_from_module_name(self, module_name):
        """ Find all tests in a module by module name """
        module = None
        module_name = ".".join([self.start_modname, module_name])
        try:
            module = __import__(module_name, {}, {}, [""])
        except ImportError, e:
            raise ImportError("Couldn't load test module: %s" %(e,))

        modtests = self.testloader(module)
        list_of_tests = getattr(modtests, self.suite_testlist_attr)
        [self.add_test(test) for test in list_of_tests]

    def iterfindmodules(self):
        """ Iterator finding all modules """
        for root, dirs, files in os.walk(self.start):
            mod_root = root.replace(self.start, "")
            for filename in files:
                if self.file_is_test_module(filename):
                    yield self.path_to_module(os.path.join(mod_root, filename))
            for dirname in dirs:
                if self.dir_is_test_module(dirname, root):
                    yield self.path_to_module(os.path.join(mod_root, dirname))
