#!/usr/bin/python -u
import glob, imp, os, sys, unittest


def find_test_files(which=__file__):
    files = glob.glob('%s/test_*py' % os.path.dirname(which))
    return [name for name in files if name != which]


def load_modules(files):
    load = imp.load_module
    find = imp.find_module
    basename = os.path.basename
    dirname = os.path.dirname
    splitext = os.path.splitext
    
    modules = []
    for filename in files:
        base = splitext(basename(filename))[0]
        filedirs = [dirname(filename), ]
        modules.append( load(base, *find(base, filedirs)) )
    return modules


def make_suite(modules):
    suite = unittest.TestSuite()
    loadfunc = unittest.defaultTestLoader.loadTestsFromModule

    for module in modules:
        cases = loadfunc(module)
        for test in cases._tests:
            suite.addTest(test)
    return suite


# for setuptools
def suite():
    return make_suite( load_modules( find_test_files() ))


if __name__ == '__main__':
    verbose = (('-v' in sys.argv) and 2) or 1
    runner = unittest.TextTestRunner(sys.stdout, 1, verbose)
    runner.run(suite())
