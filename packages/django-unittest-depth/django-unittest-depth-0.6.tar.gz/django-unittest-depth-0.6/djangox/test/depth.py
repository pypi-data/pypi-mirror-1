import os
import sys
import unittest

VERSION = (0, 6)
__version__ = ".".join(map(str, VERSION))

def alltests(*args, **kwargs):
    return DepthTestRunner(*args, **kwargs).alltests()

TEST_MODULE_REGISTRY = set()
class DepthTestRunner(object):

    suite_cls = unittest.TestSuite
    testloader = unittest.defaultTestLoader.loadTestsFromModule
    suite_testlist_attr = "_tests"
    suite_add_test_funcname = "addTest"

    def __init__(self, start, start_modname, **kwargs):
        self.start = os.path.dirname(start)
        self.start_modname = start_modname
        self.suite_cls = kwargs.get("suite_cls", self.suite_cls)
        self.suite = kwargs.get("suite", self.suite_cls())
    
    def alltests(self):
        [self.add_tests_from_module_name(module_name)
            for module_name in self.iterfindmodules()]
        return self.suite

    def add_test(self, test):
        addtest_func = getattr(self.suite, self.suite_add_test_funcname)
        addtest_func(test)

    def path_to_module(self, path):
        path = path.strip(os.path.sep)
        path = path.replace(".py", "")
        path = path.replace(os.path.sep, ".")
        return path

    def dir_is_test_module(self, dirname, root):
        is_module = os.path.exists(os.path.join(root, dirname, "__init__.py"))
        return dirname.startswith("test") and is_module
    
    def file_is_test_module(self, filename):
        return filename.startswith("test") and filename.endswith(".py")

    def add_tests_from_module_name(self, module_name):
        module = None
        module_name = ".".join([self.start_modname, module_name])
        if module_name in TEST_MODULE_REGISTRY:
            return
        TEST_MODULE_REGISTRY.add(module_name)
        try:
            module = __import__(module_name, {}, {}, [""])
        except ImportError, e:
            raise ImportError("Couldn't load test module: %s" %(e,))

        modtests = self.testloader(module)
        list_of_tests = getattr(modtests, self.suite_testlist_attr)
        [self.add_test(test) for test in list_of_tests]

    def iterfindmodules(self):
        for root, dirs, files in os.walk(self.start):
            mod_root = root.replace(self.start, "")
            for filename in files:
                if self.file_is_test_module(filename):
                    yield self.path_to_module(os.path.join(mod_root, filename))
            for dirname in dirs:
                if self.dir_is_test_module(dirname, root):
                    yield self.path_to_module(os.path.join(mod_root, dirname))
